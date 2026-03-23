/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      boxShadow: {
        enterprise: "0 18px 60px rgba(2,6,23,0.55)",
      },
    },
  },
  plugins: [],
};
