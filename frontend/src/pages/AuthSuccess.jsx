import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AuthSuccess = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setGoogleAuth } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('token');
    const name = params.get('name');
    const email = params.get('email');
    const id = params.get('id');

    if (token && name) {
      // ✅ first set the auth context with the token and user info
      setGoogleAuth(token, { id, name, email });

      // ✅ Then redirect to home after a short delay
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 500);
    } else {
      navigate('/login', { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#060b18',
      flexDirection: 'column',
      gap: '16px'
    }}>
      {/* ✅ Loading spinner */}
      <div style={{
        width: '48px',
        height: '48px',
        border: '4px solid rgba(255,255,255,0.1)',
        borderTop: '4px solid #60a5fa',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <p style={{
        color: 'white',
        fontSize: '16px',
        fontWeight: '600',
        fontFamily: 'Syne, sans-serif',
      }}>Signing you in...</p>
      <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '13px' }}>
        Please wait
      </p>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AuthSuccess;