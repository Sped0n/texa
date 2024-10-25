import { atom, computed } from "nanostores";

import { setContent } from "./editor";
import { setErrMsg } from "./msg";

// pywebviewReady
export const $pywebviewReady = atom(false);

export const setPywebviewReady = (ready: boolean) => {
	$pywebviewReady.set(ready);
};

// file state
export const $isEncoderExist = atom(false);
export const $isDecoderExist = atom(false);
export const $isTokenizerExist = atom(false);

export const $isModelExist = computed(
	[$isEncoderExist, $isDecoderExist, $isTokenizerExist],
	(encoder, decoder, tokenizer) => {
		return encoder && decoder && tokenizer;
	},
);

const setIsModelExist = (status: {
	encoder: boolean;
	decoder: boolean;
	tokenizer: boolean;
}) => {
	$isEncoderExist.set(status.encoder);
	$isDecoderExist.set(status.decoder);
	$isTokenizerExist.set(status.tokenizer);
};

export const updateIsModelExist = async () => {
	const fileStatus = await window.pywebview.api.get_file_status();
	setIsModelExist(fileStatus);
};

// globalState
type State =
	| "Waiting for pywebview"
	| "No model"
	| "Importing model"
	| "Import failed"
	| "Removing model"
	| "Remove failed"
	| "Downloading model"
	| "Download failed"
	| "Initializing"
	| "Initialized failed"
	| "Idle"
	| "Inferencing"
	| "Inference failed";

export const $globalState = atom<State>("Waiting for pywebview");

export const setGlobalState = (state: State) => {
	$globalState.set(state);
};

export const $runnable = computed($globalState, (state) => {
	return state === "Idle" || state === "Inference failed";
});

export const $isRunning = computed($globalState, (state) => {
	return state === "Inferencing";
});

export const $isDownloading = computed($globalState, (state) => {
	return state === "Downloading model";
});

export const infer = async (dataUrl: string) => {
	if (!$runnable.get()) return;
	setGlobalState("Inferencing");
	const result = await window.pywebview.api.infer(dataUrl);
	if (result.type === "ok") {
		setContent(result.data, true);
		setGlobalState("Idle");
	} else {
		setErrMsg(result.data);
		setGlobalState("Inference failed");
	}
};
