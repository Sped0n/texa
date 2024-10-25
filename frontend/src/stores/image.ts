import { atom, computed } from "nanostores";

// hide
export const $hide = atom(false);

export const setHide = (value: boolean) => {
	$hide.set(value);
};

// imageDataUrl
export const $imageDataUrl = atom<string | undefined>(undefined);
export const $isImageUndefined = computed(
	$imageDataUrl,
	(imageDataUrl) => imageDataUrl === undefined,
);

export const setImageDataUrl = (value: string | undefined) => {
	$imageDataUrl.set(value);
};
