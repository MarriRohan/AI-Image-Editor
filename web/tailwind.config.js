/**** Tailwind toolchain config (keeps original styles file intact) ****/
module.exports = {
  content: ['./index.html','./src/**/*.{js,jsx,ts,tsx}','./public/index.html','./src/styles/**/*.{js,jsx,ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
