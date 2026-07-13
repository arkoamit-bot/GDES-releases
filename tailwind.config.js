/** Tailwind build config for the BGDDR registry.
 *  Scans the Django templates so only used classes are emitted. */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./*/templates/**/*.html",
    "./node_modules/flowbite/**/*.js",
  ],
  // Safelist a few classes that only appear via server data / dynamic strings.
  safelist: [
    "chip", "ok", "todo", "warn", "danger",
    "msg", "success", "error", "warning", "info",
  ],
  theme: {
    extend: {
      colors: {
        // BADAS DKD sky-blue accent (HSL 199 88% 48% ≈ #0ea5e9) — tuned so the
        // 600 weight used on buttons reads as the bright BADAS primary.
        primary: {
          50: "#eff8ff", 100: "#dbeefe", 200: "#b9e0fe", 300: "#7cc8fd",
          400: "#36aef9", 500: "#0ea5e9", 600: "#0c92d4", 700: "#0a76ab",
          800: "#0d6391", 900: "#114e74",
        },
      },
      fontFamily: { sans: ["Inter", "Segoe UI", "Roboto", "Arial", "sans-serif"] },
    },
  },
  plugins: [require("flowbite/plugin")],
};
