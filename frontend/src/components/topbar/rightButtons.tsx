import { Icon } from "@iconify-icon/solid";
import type { JSXElement } from "solid-js";

const RightButtons = (): JSXElement => {
	const minimizeHandler = async () => {
		await window.pywebview.api.minimize();
	};

	const quitHandler = async () => {
		await window.pywebview.api.quit();
	};

	return (
		<div class="flex items-center space-x-2 flex-1 justify-end">
			<button
				type="button"
				class="px-1 pt-1 mb-1 hover:bg-gray-200 rounded"
				onClick={minimizeHandler}
			>
				<Icon
					icon="flowbite:minimize-outline"
					inline
					width="1.2em"
					height="1.2em"
				/>
			</button>
			<button
				type="button"
				class="px-1 pt-1 mb-1 text-red-600 hover:bg-gray-200 rounded"
				onClick={quitHandler}
			>
				<Icon
					icon="flowbite:arrow-right-to-bracket-outline"
					inline
					width="1.2em"
					height="1.2em"
				/>
			</button>
		</div>
	);
};

export default RightButtons;
