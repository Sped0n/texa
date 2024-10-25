import { Icon } from "@iconify-icon/solid";
import { useStore } from "@nanostores/solid";
import type { gsap as gsapType } from "gsap";
import { Show, createEffect, createSignal, on, onMount } from "solid-js";
import invariant from "tiny-invariant";

import { $content, setContent } from "../stores/editor";
import { $hide } from "../stores/image";
import { $vhpx } from "../stores/window";

const Editor = () => {
	let containerRef: HTMLDivElement | undefined;

	const [copied, setCopied] = createSignal(false);
	const hide = useStore($hide);
	const vhpx = useStore($vhpx);
	const content = useStore($content);

	let gsap: typeof gsapType | undefined = undefined;

	const copyContent = async () => {
		try {
			await navigator.clipboard.writeText(content());
			setCopied(true);
			setTimeout(() => setCopied(false), 3000);
		} catch (err) {
			console.error("Failed to copy text: ", err);
		}
	};

	onMount(async () => {
		invariant(containerRef, "containerRef is not defined");
		gsap = await import("gsap").then((module) => module.gsap);
		invariant(gsap, "gsap is not defined");
		gsap.set(containerRef, {
			height: hide()
				? `${Math.floor((vhpx() - 88) * 0.4)}px`
				: `${Math.floor((vhpx() - 44) * 0.3)}px`,
		});
	});

	createEffect(
		on(
			() => vhpx(),
			() => {
				if (!containerRef || !gsap) return;
				gsap.set(containerRef, {
					height: hide()
						? `${Math.floor((vhpx() - 88) * 0.4)}px`
						: `${Math.floor((vhpx() - 44) * 0.3)}px`,
				});
			},
			{ defer: true },
		),
	);

	createEffect(
		on(
			() => hide(),
			() => {
				if (!containerRef || !gsap) return;
				gsap.to(containerRef, {
					height: hide()
						? `${Math.floor((vhpx() - 88) * 0.4)}px`
						: `${Math.floor((vhpx() - 44) * 0.3)}px`,
					duration: 0.3,
					ease: "power3.inOut",
				});
			},
			{ defer: true },
		),
	);

	return (
		<div ref={containerRef} class="w-full h-fit py-4 flex flex-row">
			<div class="h-full w-14 relative pywebview-drag-region" />
			<div class="h-full relative grow">
				<textarea
					class="no-scrollbar w-full h-full resize-none py-4 pr-6 pl-4 border border-gray-300 rounded-md shadow-sm focus:ring-1 focus:ring-blue-300 focus:border-blue-300"
					placeholder="Start typing..."
					value={content()}
					onInput={(e) => setContent(e.currentTarget.value)}
					onWheel={(e) => e.stopPropagation()}
					onTouchMove={(e) => e.stopPropagation()}
					onPaste={(e) => e.stopPropagation()}
				/>
				<button
					type="button"
					onClick={copied() ? undefined : copyContent}
					class="absolute top-3 right-3 py-1 px-2 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
					title="Copy to clipboard"
				>
					<Show
						when={!copied()}
						fallback={
							<Icon
								icon="flowbite:check-outline"
								inline
								class="text-green-500"
							/>
						}
					>
						<Icon icon="flowbite:file-copy-outline" inline />
					</Show>
				</button>
			</div>
			<div class="h-full w-14 relative pywebview-drag-region" />
		</div>
	);
};

export default Editor;
