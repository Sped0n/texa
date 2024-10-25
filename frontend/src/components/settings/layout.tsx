import { useStore } from "@nanostores/solid";
import { gsap } from "gsap";
import { createEffect, createSignal, on, onMount } from "solid-js";
import invariant from "tiny-invariant";

import Advanced from "./advanced";
import ModelMgr from "./modelMgr";

import { $isSettingsOpen, setIsSettingsOpen } from "../../stores/settings";

const Settings = () => {
	let modalRef: HTMLDivElement | undefined;
	let overlayRef: HTMLDivElement | undefined;

	const [isAnimating, setIsAnimating] = createSignal(false);
	const isSettingsOpen = useStore($isSettingsOpen);

	const animateIn = () => {
		invariant(overlayRef, "overlayRef is not defined");
		invariant(modalRef, "modalRef is not defined");
		setIsAnimating(true);
		const tl = gsap.timeline();
		tl.to(overlayRef, { opacity: 1, duration: 0.3, display: "flex" });
		tl.to(
			modalRef,
			{ scale: 1, opacity: 1, duration: 0.3, ease: "power3.inOut" },
			"-=0.1",
		);
		tl.then(() => {
			setIsAnimating(false);
		});
	};

	const animateOut = () => {
		invariant(modalRef, "modalRef is not defined");
		invariant(overlayRef, "overlayRef is not defined");
		setIsAnimating(true);
		const tl = gsap.timeline();
		tl.to(modalRef, { scale: 0.8, opacity: 0, duration: 0.2 });
		tl.to(overlayRef, { opacity: 0, duration: 0.2, display: "none" }, "-=0.1");
		tl.then(() => {
			setIsSettingsOpen(false);
			setIsAnimating(false);
		});
	};

	const handleOverlayClick = (e: MouseEvent) => {
		if (e.target === e.currentTarget) {
			animateOut();
		}
	};

	onMount(() => {
		invariant(modalRef, "modalRef is not defined");
		invariant(overlayRef, "overlayRef is not defined");
		gsap.set(modalRef, { scale: 0.8, opacity: 0 });
		gsap.set(overlayRef, { opacity: 0, display: "none" });
	});

	createEffect(
		on(
			() => isSettingsOpen(),
			() => {
				if (isSettingsOpen() && !isAnimating()) {
					animateIn();
				}
			},
			{ defer: false },
		),
	);

	return (
		// biome-ignore lint/a11y/useKeyWithClickEvents: <explanation>
		<div
			ref={overlayRef}
			class="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full items-center justify-center"
			style="display: none;"
			onClick={handleOverlayClick}
		>
			<div
				ref={modalRef}
				class="p-8 bg-white shadow-xl rounded-lg w-[32rem] max-w-full"
			>
				<ModelMgr />
				<Advanced />
			</div>
		</div>
	);
};

export default Settings;
