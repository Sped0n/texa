import { useStore } from "@nanostores/solid";
import gsap from "gsap";
import { type JSXElement, createEffect, on, onMount } from "solid-js";
import invariant from "tiny-invariant";
import "katex/dist/katex.min.css";

import { $debouncedContent } from "../stores/editor";
import { $hide } from "../stores/image";
import { $vhpx } from "../stores/window";

import { mdConvert } from "../helpers";

const Result = (): JSXElement => {
	let containerRef: HTMLDivElement | undefined;
	let mdtexRender: HTMLDivElement | undefined;

	const hideOriginal = useStore($hide);
	const vhpx = useStore($vhpx);
	const debouncedContent = useStore($debouncedContent);

	onMount(() => {
		invariant(containerRef, "containerRef is not defined");
		gsap.set(containerRef, {
			height: hideOriginal()
				? `${Math.floor((vhpx() - 88) * 0.6)}px`
				: `${Math.floor((vhpx() - 44) * 0.3)}px`,
		});
	});

	createEffect(
		on(
			() => vhpx(),
			() => {
				invariant(containerRef, "containerRef is not defined");
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
				invariant(containerRef, "containerRef is not defined");
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
		invariant(mdtexRender, "mdtexRender is not defined");
		mdtexRender.innerHTML = mdConvert(debouncedContent());
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
