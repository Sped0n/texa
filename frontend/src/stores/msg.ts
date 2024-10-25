import { atom } from "nanostores";

export const $errMsg = atom("");

export const setErrMsg = (msg: string) => {
	$errMsg.set(msg);
};
