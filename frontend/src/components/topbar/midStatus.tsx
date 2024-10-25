import { Icon } from "@iconify-icon/solid";
import { useStore } from "@nanostores/solid";
import type { gsap as gsapType } from "gsap";
import { type JSXElement, createMemo, createSignal, onMount } from "solid-js";
import invariant from "tiny-invariant";

import { $errMsg } from "../../stores/msg";
import { $globalState } from "../../stores/states";

const MidStatus = (): JSXElement => {
	let popoverRef: HTMLDivElement | undefined;
	let statusRef: HTMLDivElement | undefined;

	const globalState = useStore($globalState);
	const [showPopover, setShowPopover] = createSignal(false);
	const errMsg = useStore($errMsg);

	let gsap: typeof gsapType | undefined = undefined;

	const handleClickOutside = (event: MouseEvent) => {
		if (popoverRef && !popoverRef.contains(event.target as Node)) {
			setShowPopover(false);
		}
	};

	const hasError = createMemo(() => {
		const state = globalState();
		return state.toLowerCase().includes("failed");
	});

	const hasIng = createMemo(() => {
		const state = globalState();
		return state.toLowerCase().includes("ing");
	});

	const togglePopover = (event: MouseEvent) => {
		if (!hasError() || !gsap) return;
		event.stopPropagation();
		setShowPopover(!showPopover());
		invariant(popoverRef, "popoverRef is not defined");
		if (!showPopover()) {
			gsap.to(popoverRef, {
				opacity: 0,
				y: -10,
				duration: 0.2,
				ease: "power2.out",
			});
		} else {
			gsap.fromTo(
				popoverRef,
				{ opacity: 0, y: -10 },
				{ opacity: 1, y: 0, duration: 0.2, ease: "power2.out" },
			);
		}
	};

	onMount(async () => {
		gsap = await import("gsap").then((module) => module.gsap);
		window.addEventListener("click", handleClickOutside);
	});

	return (
		<div ref={statusRef} class="status text-center flex-1 relative">
			{/* biome-ignore lint/a11y/useKeyWithClickEvents: <explanation> */}
			<span
				class={`font-normal ${hasError() ? "text-red-500 cursor-pointer" : ""}`}
				onClick={togglePopover}
			>
				{globalState()}
				{hasError() && <Icon icon="line-md:alert" inline class="ml-1" />}
				{hasIng() && (
					<Icon icon="line-md:loading-twotone-loop" inline class="ml-1" />
				)}
			</span>
			{hasError() && showPopover() && (
				<div
					ref={popoverRef}
					class="text-sm absolute z-20 w-96 bg-white border border-gray-200 rounded-lg shadow-lg p-3 mt-4 left-1/2 transform -translate-x-1/2"
					style="opacity: 0"
				>
					<div class="absolute w-6 h-6 bg-white border-t border-l border-gray-200 -top-3 left-1/2 transform -translate-x-1/2 rotate-45" />
					<div class="mb-2">click to copy error message</div>
					{/* biome-ignore lint/a11y/useKeyWithClickEvents: <explanation> */}
					<div
						class="text-wrap text-red-500 border border-red-200 p-2 rounded bg-red-200 cursor-pointer"
						onClick={async () => await navigator.clipboard.writeText(errMsg())}
					>
						<u>{errMsg()}</u>
					</div>
				</div>
			)}
		</div>
	);
};

export default MidStatus;
