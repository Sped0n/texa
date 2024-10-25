import { debounce } from "@solid-primitives/scheduled";
import { atom } from "nanostores";

export const $debouncedContent = atom("");
export const $content = atom("");

const debouncedSetContent = debounce((value: string) => {
	setDebouncedContent(value);
}, 250);

export const setDebouncedContent = (value: string) => {
	$debouncedContent.set(value);
};

export const setContent = (value: string, direct = false) => {
	$content.set(value);
	if (direct) {
		$debouncedContent.set(value);
	} else {
		debouncedSetContent(value);
	}
};
