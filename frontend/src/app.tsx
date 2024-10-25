import { useStore } from "@nanostores/solid";
import { createEffect, onMount } from "solid-js";

import Editor from "./components/editor";
import Image from "./components/image";
import Result from "./components/result";
import Settings from "./components/settings/layout";
import TopBar from "./components/topbar/layout";

import { setImageDataUrl } from "./stores/image";
import { setErrMsg } from "./stores/msg";
import {
	$isModelExist,
	$pywebviewReady,
	$runnable,
	infer,
	setGlobalState,
	setPywebviewReady,
	updateIsModelExist,
} from "./stores/states";
import { setVhpx } from "./stores/window";

const App = () => {
	const pywebviewReady = useStore($pywebviewReady);
	const runnable = useStore($runnable);
	const isModelExist = useStore($isModelExist);

	const pasteHandler = async (event: ClipboardEvent) => {
		if (event.clipboardData === null) return;
		if (!runnable()) return;
		const reader = new FileReader();
		reader.onloadend = async () => {
			setImageDataUrl(reader.result as string);
			await infer(reader.result as string);
		};
		for (const file of event.clipboardData.files) {
			if (!file.type.startsWith("image/")) continue;
			reader.readAsDataURL(file);
			break;
		}
	};

	onMount(() => {
		window.addEventListener("resize", () => {
			setVhpx();
		});
		window.addEventListener("paste", pasteHandler);
		if (window.pywebview !== undefined) {
			setTimeout(() => {
				setPywebviewReady(true);
			}, 100); // delay to prevent start up lag
		} else {
			window.addEventListener(
				"pywebviewready",
				() => {
					setTimeout(() => {
						setPywebviewReady(true);
					}, 100); // delay to prevent start up lag
				},
				{ once: true },
			);
		}
	});

	createEffect(async () => {
		if (!pywebviewReady()) return;
		await updateIsModelExist();
	});

	createEffect(async () => {
		if (!isModelExist()) {
			setGlobalState("No model");
			return;
		}
		setGlobalState("Initializing");
		const result = await window.pywebview.api.init_pipeline();
		if (result.type === "ok") {
			setGlobalState("Idle");
		} else {
			setErrMsg(result.data);
			setGlobalState("Initialized failed");
		}
	});

	return (
		<div class="h=fit min-h-screen bg-gray-100 font-sans font-medium flex flex-col">
			<TopBar />
			<div class="flex-grow flex flex-col overflow-hidden">
				<Image />
				<Result />
				<Editor />
			</div>
			<Settings />
		</div>
	);
};

export default App;
