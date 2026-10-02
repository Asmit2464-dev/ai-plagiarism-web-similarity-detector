const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const User = require('../models/User');

passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID',
    clientSecret: process.env.GOOGLE_CLIENT_SECRET || 'YOUR_GOOGLE_CLIENT_SECRET',
    callbackURL: 'http://localhost:5000/api/auth/google/callback',
}, async (accessToken, refreshToken, profile, done) => {
    try {
        // ✅ Check if user already exists with Google ID
        let user = await User.findOne({ googleId: profile.id });

        if (!user) {
            // ✅ If user doesn't exist, check if there's a user with the same email
            user = await User.findOne({ email: profile.emails[0].value });

            if (user) {
                // ✅ Existing user ko Google ID link karo
                user.googleId = profile.id;
                user.avatar = profile.photos[0]?.value;
                await user.save();
            } else {
                // ✅ create new user if not found
                user = await User.create({
                    name: profile.displayName,
                    email: profile.emails[0].value,
                    googleId: profile.id,
                    avatar: profile.photos[0]?.value,
                });
            }
        }
        return done(null, user);
    } catch (err) {
        return done(err, null);
    }
}));

passport.serializeUser((user, done) => done(null, user._id));
passport.deserializeUser(async (id, done) => {
    try {
        const user = await User.findById(id);
        done(null, user);
    } catch (err) {
        done(err, null);
    }
});