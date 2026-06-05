export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        shell: "#08111b",
        panel: "#102134",
        line: "#26435f",
        accent: "#7dd3fc",
        success: "#86efac",
        warning: "#fde68a",
        danger: "#fca5a5"
      },
      boxShadow: {
        glow: "0 18px 80px rgba(16, 33, 52, 0.45)"
      },
      fontFamily: {
        display: ["ui-sans-serif", "system-ui", "sans-serif"]
      }
    },
  },
  plugins: [],
};
