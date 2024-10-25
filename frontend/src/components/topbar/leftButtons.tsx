import { Icon } from "@iconify-icon/solid";
import { useStore } from "@nanostores/solid";
import { type JSXElement, createMemo } from "solid-js";

import { setContent } from "../../stores/editor";
import {
	$imageDataUrl,
	$isImageUndefined,
	setImageDataUrl,
} from "../../stores/image";
import { setErrMsg } from "../../stores/msg";
import { setIsSettingsOpen } from "../../stores/settings";
import {
	$isRunning,
	$pywebviewReady,
	$runnable,
	infer,
	setGlobalState,
} from "../../stores/states";

const LeftButtons = (): JSXElement => {
	const imageDataUrl = useStore($imageDataUrl);
	const runnable = useStore($runnable);
	const isImageUndefined = useStore($isImageUndefined);
	const pywebviewReady = useStore($pywebviewReady);
	const isRunning = useStore($isRunning);

	const rerunnable = createMemo(() => {
		return runnable() && !isImageUndefined();
	});
	const settingsUsable = createMemo(() => {
		return pywebviewReady() && !isRunning();
	});

	const uploadHandler = async () => {
		if (!runnable()) return;
		const result = await window.pywebview.api.open_image();
		if (result.type === "ok") {
			if (result.data === "user cancelled") return;
			setImageDataUrl(result.data);
			await infer(result.data);
		} else {
			setErrMsg(result.data);
			setGlobalState("Inference failed");
		}
	};

	const rerunHandler = async () => {
		if (!rerunnable()) return;
		await infer(imageDataUrl() as string);
	};

	const clearHandler = () => {
		if (isImageUndefined()) return;
		setContent("", true);
		setImageDataUrl(undefined);
	};

	return (
		<div class="flex items-center space-x-2 flex-1">
			<button
				type="button"
				class={`px-1 pt-1 mb-1 rounded ${runnable() ? "hover:bg-gray-200" : "text-gray-400"}`}
				onClick={uploadHandler}
				disabled={!runnable()}
			>
				<Icon
					icon="flowbite:file-circle-plus-outline"
					inline
					width="1.2em"
					height="1.2em"
				/>
			</button>
			<button
				type="button"
				class={`px-1 pt-1 mb-1 rounded ${rerunnable() ? "hover:bg-gray-200" : "text-gray-400"}`}
				onClick={rerunHandler}
				disabled={!rerunnable()}
			>
				<Icon
					icon="flowbite:redo-outline"
					inline
					width="1.2em"
					height="1.2em"
				/>
			</button>
			<button
				type="button"
				class={`px-1 pt-1 mb-1 rounded ${rerunnable() ? "hover:bg-gray-200" : "text-gray-400"}`}
				onClick={clearHandler}
				disabled={!rerunnable()}
			>
				<Icon
					icon="flowbite:trash-bin-outline"
					inline
					width="1.2em"
					height="1.2em"
				/>
			</button>
			<button
				type="button"
				class={`px-1 pt-1 mb-1 rounded ${settingsUsable() ? "hover:bg-gray-200" : "text-gray-400"}`}
				onClick={() => setIsSettingsOpen(true)}
				disabled={!settingsUsable()}
			>
				<Icon
					icon="flowbite:adjustments-horizontal-outline"
					inline
					width="1.2em"
					height="1.2em"
				/>
			</button>
		</div>
	);
};

export default LeftButtons;
