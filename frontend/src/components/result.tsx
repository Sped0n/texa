import { useStore } from "@nanostores/solid";
import type { gsap as gsapType } from "gsap";
import { type JSXElement, createEffect, on, onMount } from "solid-js";
import invariant from "tiny-invariant";

import { $debouncedContent } from "../stores/editor";
import { $hide } from "../stores/image";
import { $vhpx } from "../stores/window";

const Result = (): JSXElement => {
	let containerRef: HTMLDivElement | undefined;
	let mdtexRender: HTMLDivElement | undefined;

	const hideOriginal = useStore($hide);
	const vhpx = useStore($vhpx);
	const debouncedContent = useStore($debouncedContent);

	let converter: ((content: string) => string) | undefined = undefined;
	let gsap: typeof gsapType | undefined = undefined;

	onMount(async () => {
		invariant(containerRef, "containerRef is not defined");
		gsap = await import("gsap").then((module) => module.gsap);
		invariant(gsap, "gsap is not defined");
		gsap.set(containerRef, {
			height: hideOriginal()
				? `${Math.floor((vhpx() - 88) * 0.6)}px`
				: `${Math.floor((vhpx() - 44) * 0.3)}px`,
		});
		converter = await import("../converter").then((module) => module.mdConvert);
		await import("katex/dist/katex.min.css");
	});

	createEffect(
		on(
			() => vhpx(),
			() => {
				if (!containerRef || !gsap) return;
				gsap.set(containerRef, {
					height: hideOriginal()
						? `${Math.floor((vhpx() - 88) * 0.6)}px`
						: `${Math.floor((vhpx() - 44) * 0.3)}px`,
				});
			},
			{ defer: true },
		),
	);

	createEffect(
		on(
			() => hideOriginal(),
			() => {
				if (!containerRef || !gsap) return;
				gsap.to(containerRef, {
					height: hideOriginal()
						? `${Math.floor((vhpx() - 88) * 0.6)}px`
						: `${Math.floor((vhpx() - 44) * 0.3)}px`,
					duration: 0.3,
					ease: "power3.inOut",
				});
			},
			{ defer: true },
		),
	);

	createEffect(() => {
		const content = debouncedContent(); // weird bug, it seems solid cannot recognize debouncedContent() as a dependency when I put it in the converter function
		if (!mdtexRender || !converter) return;
		mdtexRender.innerHTML = converter(content);
		console.log("mdtexRender", converter(debouncedContent()));
		mdtexRender.appendChild(document.createElement("br"));
	});

	return (
		<div
			ref={containerRef}
			class="bg-white border-b border-gray-300 overflow-y-auto py-4 flex flex-row justify-center pywebview-drag-region"
			onWheel={(e) => e.stopPropagation()}
			onTouchMove={(e) => e.stopPropagation()}
		>
			<div
				class="px-4 prose prose-sm prose-lead:leading-tight"
				ref={mdtexRender}
			/>
		</div>
	);
};

export default Result;
