/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      "./app/templates/**/*.html",
      "./app/static/src/**/*.js",
      "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
        colors: {
            "base-french-gray": "#fafbf8",
            "accent-1-slate": "#4b4f4e",
            "accent-2-space-cadet": "#4b4f4e",
            "accent-2-space-cadet-li": "rgba(75,79,78,0.76)",
            "accent-3-reddish": "#ef6334",
            "accent-4-orange-5": "#FF922B",
            "text-1-almost-black": "#111316"
        }
    },
  },
  plugins: [
       require("flowbite/plugin")
  ],
}

