import { atom } from "nanostores";

export const $isSettingsOpen = atom(false);

export function setIsSettingsOpen(value: boolean) {
	$isSettingsOpen.set(value);
}
