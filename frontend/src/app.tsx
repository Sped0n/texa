import { useStore } from "@nanostores/solid";
import {
	Show,
	createEffect,
	createMemo,
	createSignal,
	onMount,
} from "solid-js";

import Editor from "./components/editor";
import Image from "./components/image";
import Result from "./components/result";
import Settings from "./components/settings/layout";
import TopBar from "./components/topbar/layout";

import { setImageDataUrl } from "./stores/image";
import { setErrMsg } from "./stores/msg";
import { $isSettingsOpen } from "./stores/settings";
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
	const isSettingsOpen = useStore($isSettingsOpen);
	const [isDragging, setIsDragging] = createSignal(false);

	const dragEnabled = createMemo(() => {
		return !isSettingsOpen() && isDragging();
	});

	const handleFile = async (file: File) => {
		if (!runnable()) return;
		if (!file.type.startsWith("image/")) return;

		const reader = new FileReader();
		reader.onloadend = async () => {
			setImageDataUrl(reader.result as string);
			await infer(reader.result as string);
		};
		reader.readAsDataURL(file);
	};

	const pasteHandler = async (e: ClipboardEvent) => {
		e.preventDefault();
		if (e.clipboardData === null) return;
		if (!runnable()) return;

		for (const file of e.clipboardData.files) {
			if (!file.type.startsWith("image/")) continue;
			await handleFile(file);
			break;
		}
	};

	const dragEnterHandler = (e: DragEvent) => {
		e.preventDefault();
		setIsDragging(true);
	};

	const dragLeaveHandler = (e: DragEvent) => {
		e.preventDefault();
		setIsDragging(false);
	};

	const dragOverHandler = (e: DragEvent) => {
		e.preventDefault();
		setIsDragging(true);
	};

	const dropHandler = async (e: DragEvent) => {
		e.preventDefault();
		setIsDragging(false);

		if (!e.dataTransfer) return;
		const file = e.dataTransfer.files[0];
		if (file) {
			await handleFile(file);
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
			}, 100);
		} else {
			window.addEventListener(
				"pywebviewready",
				() => {
					setTimeout(() => {
						setPywebviewReady(true);
					}, 100);
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
		<div
			class="h-fit min-h-screen bg-gray-100 font-sans font-medium flex flex-col relative"
			onDragEnter={dragEnterHandler}
			onDragLeave={dragLeaveHandler}
			onDragOver={dragOverHandler}
			onDrop={dropHandler}
		>
			<Show when={dragEnabled()}>
				<div class="absolute inset-0 bg-blue-900 bg-opacity-75 flex items-center border-dashed border-white border-4 rounded-lg justify-center z-10 pointer-events-none">
					<p class="text-white font-bold text-3xl">Drop image here</p>
				</div>
			</Show>
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
