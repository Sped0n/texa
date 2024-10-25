import { Icon } from "@iconify-icon/solid";
import type { gsap as gsapType } from "gsap";
import {
	type Accessor,
	type JSXElement,
	createSignal,
	onMount,
} from "solid-js";

import {
	$globalState,
	$isDownloading,
	setGlobalState,
	updateIsModelExist,
} from "../../stores/states";

import { useStore } from "@nanostores/solid";
import invariant from "tiny-invariant";
import { nameToFileType } from "../../helpers";
import { setErrMsg } from "../../stores/msg";

interface FileStatusProps {
	name: "Encoder Model" | "Decoder Model" | "Tokenizer";
	icon: string;
	isImported: Accessor<boolean>;
}

export const FileStatus = (props: FileStatusProps): JSXElement => {
	let buttonRef: HTMLButtonElement | undefined;

	const [isPressed, setIsPressed] = createSignal(false);
	const globalState = useStore($globalState);
	const isDownloading = useStore($isDownloading);

	let gsap: typeof gsapType | undefined = undefined;

	const importHandler = async () => {
		if (isPressed()) {
			setIsPressed(false);
			return;
		}
		if (props.isImported()) return;
		const prevGlobalState = globalState();
		setGlobalState("Importing model");
		const result = await window.pywebview.api.import_file(
			nameToFileType(props.name),
		);
		if (result.type === "ok") {
			if (result.data === "user cancelled") {
				setGlobalState(prevGlobalState);
			} else {
				await updateIsModelExist();
			}
		} else {
			setErrMsg(result.data);
			setGlobalState("Import failed");
		}
	};

	const removeHandler = async () => {
		if (!props.isImported()) return;
		await window.pywebview.api.destroy_pipeline();
		setGlobalState("Removing model");
		const result = await window.pywebview.api.remove_file(
			nameToFileType(props.name),
		);
		if (result.type === "ok") {
			await updateIsModelExist();
		} else {
			setErrMsg(result.data);
			setGlobalState("Remove failed");
		}
	};

	const startRemoveAnimation = () => {
		if (!props.isImported() || !buttonRef || !gsap) return;
		setIsPressed(true);
		gsap.set(buttonRef, { "--progress": "0%" });
		gsap.to(buttonRef, {
			"--progress": "100%",
			duration: 2,
			ease: "linear",
			onComplete: () => {
				removeHandler().then(() => {
					if (!gsap) return;
					gsap.set(buttonRef, { "--progress": "0%" });
				});
			},
		});
	};

	const cancelRemoveAnimation = () => {
		if (!props.isImported() || !buttonRef || !gsap) return;
		setIsPressed(false);
		gsap.killTweensOf(buttonRef);
		gsap.set(buttonRef, { "--progress": "0%" });
	};

	onMount(async () => {
		gsap = await import("gsap").then((module) => module.gsap);
		invariant(gsap, "gsap is not defined");
	});

	return (
		<div class="flex items-center justify-between p-2">
			<div class="flex items-center">
				<Icon inline icon={props.icon} width="20" height="20" />
				<div class="ml-3">
					<div
						class="flex items-center"
						title={props.isImported() ? "Imported" : "Not imported"}
					>
						<span class="text-sm font-medium">{props.name}</span>
						<span
							class={`ml-2 w-2 h-2 rounded-full ${
								props.isImported() ? "bg-green-400" : "bg-red-400"
							}`}
						/>
					</div>
				</div>
			</div>
			<button
				ref={buttonRef}
				type="button"
				onMouseDown={startRemoveAnimation}
				onMouseUp={() => {
					if (props.isImported()) {
						cancelRemoveAnimation();
					} else {
						importHandler();
					}
				}}
				onMouseLeave={cancelRemoveAnimation}
				onTouchStart={startRemoveAnimation}
				onTouchEnd={cancelRemoveAnimation}
				class={`
          w-14 py-1 text-xs rounded-md border relative bg-white text-black text-center border-gray-300
          ${isDownloading() ? "cursor-not-allowed bg-gray-100 text-gray-400" : ""}
        `}
				style={{
					"background-image": props.isImported()
						? "linear-gradient(90deg, rgb(239 68 68 / 0.2) var(--progress, 0%), transparent var(--progress, 0%))"
						: "none",
				}}
				disabled={isDownloading()}
			>
				{props.isImported() ? "Remove" : "Import"}
			</button>
		</div>
	);
};

export default FileStatus;
