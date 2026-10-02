const mongoose = require('mongoose');

const ReportSchema = new mongoose.Schema({
  // ✅ link from user
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    default: null, // null for API key users
  },

  // ✅ Text info
  text: {
    type: String,
    required: true,
  },
  textPreview: {
    type: String, // first 200 characters for quick preview
    default: '',
  },
  fileName: {
    type: String,
    default: 'Direct Input',
  },
  wordCount: {
    type: Number,
    default: 0,
  },

  // ✅ Scores
  score: {
    type: Number,
    required: true,
  },
  aiScore: {
    type: Number,
    default: 0,
  },

  // ✅ Results
  summary: {
    type: String,
    default: '',
  },
  matchedSources: {
    type: Array,
    default: [],
  },
  highlights: {
    type: Array,
    default: [],
  },

  // ✅ Options
  excludeQuotes: {
    type: Boolean,
    default: false,
  },
  excludeBibliography: {
    type: Boolean,
    default: false,
  },

  // ✅ Verdict
  verdict: {
    type: String,
    enum: ['Original', 'Medium Risk', 'High Risk'],
    default: 'Original',
  },

  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// ✅ Indexes — For faster queries
ReportSchema.index({ userId: 1 });
ReportSchema.index({ createdAt: -1 });
ReportSchema.index({ score: 1 });

module.exports = mongoose.model('Report', ReportSchema);