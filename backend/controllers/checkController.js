const Report = require('../models/Report');
const axios = require('axios');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'plagiocheck_secret_key';

// ✅ get user ID from JWT token 
const getUserFromToken = (req) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return null;
    const decoded = jwt.verify(token, JWT_SECRET);
    return decoded.id;
  } catch {
    return null;
  }
};

const checkPlagiarism = async (req, res) => {
  try {
    const { text, reference, fileName, checkAI, excludeQuotes, excludeBibliography } = req.body;

    if (!text) {
      return res.status(400).json({ message: 'Text is required!' });
    }

    // ✅ User ID fetch karo from JWT token
    const userId = getUserFromToken(req);

    // ✅ Call ML service for plagiarism check
    const ML_URL = process.env.ML_SERVICE_URL || 'http://127.0.0.1:5001';
    const mlResponse = await axios.post(`${ML_URL}/analyze`, {
      text: text,
      reference: reference || null,
      check_ai: checkAI || false,
      check_web: true,
      exclude_quotes: excludeQuotes || false,
      exclude_bibliography: excludeBibliography || false,
    });

    const { score, matched_sources, highlights, summary, ai_score } = mlResponse.data;

    // ✅ Verdict calculate karo
    const verdict = score >= 70 ? 'High Risk' : score >= 40 ? 'Medium Risk' : 'Original';

    // ✅ Report save karo MongoDB mein
    const report = new Report({
      userId: userId || null,
      text: text,
      textPreview: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
      fileName: fileName || 'Direct Input',
      wordCount: text.trim().split(/\s+/).filter(w => w.length > 0).length,
      score: score,
      aiScore: ai_score || 0,
      summary: summary || '',
      matchedSources: matched_sources || [],
      highlights: highlights || [],
      verdict: verdict,
      excludeQuotes: excludeQuotes || false,
      excludeBibliography: excludeBibliography || false,
    });

    // The checker can still be used without a local MongoDB instance; only
    // persistence features (history and saved reports) require the database.
    if (Report.db.readyState === 1) {
      await report.save();
    }

    res.status(200).json({
      success: true,
      reportId: Report.db.readyState === 1 ? report._id : null,
      score: score,
      aiScore: ai_score || 0,
      matched_sources: matched_sources,
      highlights: highlights,
      summary: summary,
      verdict: verdict,
      message: 'Plagiarism check completed!'
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ message: 'Server error!', error: error.message });
  }
};

// ✅ fetch user history from MongoDB
const getHistory = async (req, res) => {
  try {
    const userId = getUserFromToken(req);
    if (!userId) {
      return res.status(401).json({ message: 'Login karo history dekhne ke liye!' });
    }

    const reports = await Report.find({ userId })
      .sort({ createdAt: -1 })
      .limit(20)
      .select('-text -highlights'); // dont send full text and highlights for history list

    res.status(200).json({ success: true, reports });
  } catch (error) {
    res.status(500).json({ message: 'Server error!', error: error.message });
  }
};

// ✅ fetch single report by ID from MongoDB
const getReport = async (req, res) => {
  try {
    const report = await Report.findById(req.params.id);
    if (!report) {
      return res.status(404).json({ message: 'Report nahi mili!' });
    }
    res.status(200).json({ success: true, report });
  } catch (error) {
    res.status(500).json({ message: 'Server error!', error: error.message });
  }
};

module.exports = { checkPlagiarism, getHistory, getReport };
