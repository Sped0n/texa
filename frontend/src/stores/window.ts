import { atom } from "nanostores";

export const $vhpx = atom(window.innerHeight);

export function setVhpx() {
	$vhpx.set(window.innerHeight);
}
