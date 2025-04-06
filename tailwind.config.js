/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  darkMode: "class", // Enables class-based dark mode
  theme: {
    extend: {
      colors: {
        darkBg: "#1a202c", // Dark mode background
        darkText: "#e2e8f0", // Dark mode text color
      },
      transitionProperty: {
        width: "width",
        opacity: "opacity",
        background: "background",
        transform: "transform",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: 0 },
          "100%": { opacity: 1 },
        },
        slideUp: {
          "0%": { transform: "translateY(50px)", opacity: 0 },
          "100%": { transform: "translateY(0)", opacity: 1 },
        },
      },
      animation: {
        fadeIn: "fadeIn 1s ease-in-out",
        slideUp: "slideUp 0.8s ease-out",
      },
    },
  },
  plugins: [],
};


