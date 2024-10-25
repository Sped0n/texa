import { Icon } from "@iconify-icon/solid";
import { useStore } from "@nanostores/solid";
import type { gsap as gsapType } from "gsap";
import { type JSXElement, Show, createEffect, on, onMount } from "solid-js";
import invariant from "tiny-invariant";

import { $hide, setHide } from "../stores/image";
import { $imageDataUrl, $isImageUndefined } from "../stores/image";
import { $vhpx } from "../stores/window";

const Image = (): JSXElement => {
	let containerRef: HTMLDivElement | undefined;

	const hideOriginal = useStore($hide);
	const vhpx = useStore($vhpx);
	const imageDataUrl = useStore($imageDataUrl);
	const isImageUndefined = useStore($isImageUndefined);

	let gsap: typeof gsapType | undefined = undefined;

	onMount(async () => {
		invariant(containerRef, "containerRef is not defined");
		gsap = await import("gsap").then((module) => module.gsap);
		invariant(gsap, "gsap is not defined");
		gsap.set(containerRef, {
			height: hideOriginal() ? "44px" : `${Math.floor((vhpx() - 44) * 0.4)}px`,
		});
	});

	createEffect(
		on(
			() => vhpx(),
			() => {
				if (!containerRef || !gsap) return;
				gsap.set(containerRef, {
					height: hideOriginal()
						? "44px"
						: `${Math.floor((vhpx() - 44) * 0.4)}px`,
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
						? "44px"
						: `${Math.floor((vhpx() - 44) * 0.4)}px`,
					duration: 0.3,
					ease: "power3.inOut",
				});
			},
			{ defer: true },
		),
	);

	return (
		<div
			ref={containerRef}
			class="bg-white border-b border-gray-300 p-2 overflow-hidden pywebview-drag-region"
		>
			<div class="flex justify-between items-center">
				<button
					type="button"
					class="text-sm transition-colors p-1 rounded duration-150 ease-in-out hover:text-blue-600 text-gray-600"
					onClick={() => setHide(!hideOriginal())}
				>
					<div class="flex ml-1 items-center w-30">
						<span class="overflow-hidden">
							{hideOriginal() ? "Show Original" : "Hide Original"}
						</span>
						{hideOriginal() ? (
							<Icon
								icon="flowbite:eye-outline"
								inline
								class="ml-1"
								width="1.2em"
								height="1.2em"
							/>
						) : (
							<Icon
								icon="flowbite:eye-slash-outline"
								inline
								class="ml-1"
								width="1.2em"
								height="1.2em"
							/>
						)}
					</div>
				</button>
			</div>
			<div class="mt-2 flex items-center justify-center overflow-hidden h-[calc((100vh-44px)*0.4-44px)]">
				<Show
					when={!isImageUndefined()}
					fallback={
						<Icon width={36} height={36} icon="flowbite:image-outline" />
					}
				>
					<img
						class="pt-2 pb-5 px-4 object-contain h-full w-full"
						src={imageDataUrl()}
						alt="random"
					/>
				</Show>
			</div>
		</div>
	);
};

export default Image;
