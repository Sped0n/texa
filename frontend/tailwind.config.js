/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./src/**/*.{js,jsx,ts,tsx}"],
	theme: {
		fontFamily: {
			sans: ["Geist", ...require("tailwindcss/defaultTheme").fontFamily.sans],
			mono: [
				"Geist Mono",
				...require("tailwindcss/defaultTheme").fontFamily.mono,
			],
		},
	},
	plugins: [require("@tailwindcss/typography")],
};
