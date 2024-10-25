import { micromark } from "micromark";
import { math, mathHtml } from "micromark-extension-math";

export const mdConvert = (content: string): string => {
	const paragraphs: string[] = content.split("\n\n");
	let result = "";
	for (const paragraph of paragraphs) {
		try {
			result += micromark(paragraph, {
				extensions: [math()],
				htmlExtensions: [mathHtml()],
			});
		} catch (e) {
			const errorDiv = document.createElement("div");
			errorDiv.style.color = "red";
			errorDiv.style.backgroundColor = "yellow";
			errorDiv.innerHTML = micromark(paragraph);
			result += errorDiv.outerHTML;
		}
	}
	return result;
};
