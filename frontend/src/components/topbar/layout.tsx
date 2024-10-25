import type { JSXElement } from "solid-js";

import LeftButtons from "./leftButtons";
import MidStatus from "./midStatus";
import RightButtons from "./rightButtons";

const TopBar = (): JSXElement => {
	return (
		<div class="flex items-center justify-between bg-gray-100 pt-2 pb-1 px-2 border-b border-gray-300 h-11 pywebview-drag-region">
			<LeftButtons />
			<MidStatus />
			<RightButtons />
		</div>
	);
};

export default TopBar;
