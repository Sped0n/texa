import { useStore } from "@nanostores/solid";
import { type JSXElement, createMemo } from "solid-js";

import { setErrMsg } from "../../stores/msg";
import {
	$isDownloading,
	$isModelExist,
	setGlobalState,
	updateIsModelExist,
} from "../../stores/states";

const Advanced = (): JSXElement => {
	const isDownloading = useStore($isDownloading);
	const isModelExist = useStore($isModelExist);
	const notDownloadable = createMemo(() => isModelExist() || isDownloading());

	const handleDownloadModel = async () => {
		if (notDownloadable()) return;
		setGlobalState("Downloading model");
		const result = await window.pywebview.api.download_missing_model_from_hf();
		if (result.type === "ok") {
			updateIsModelExist();
		} else {
			setErrMsg(result.data);
			setGlobalState("Download failed");
		}
	};

	return (
		<div>
			<div class="font-medium text-sm mb-2 ml-3 mt-5 text-gray-600">
				Advanced
			</div>
			<div class="flex flex-col justify-between px-2 bg-gray-100 rounded-lg mb-3">
				<div class="flex items-center justify-between p-2">
					<div class="flex items-center">
						<div class="ml-1">
							<div class="flex items-center">
								<span class="text-sm font-medium">
									Download missing model(s) from
								</span>
								<img
									src="/icons/hf-logo-with-title.svg"
									alt="Hugging Face"
									class="h-7 inline"
								/>
							</div>
						</div>
					</div>
					<button
						type="button"
						onClick={handleDownloadModel}
						class={`px-2 py-1 text-xs bg-white rounded-md text-black border border-gray-300 ${notDownloadable() ? "cursor-not-allowed bg-gray-100 text-gray-400" : ""}`}
						disabled={notDownloadable()}
					>
						Download
					</button>
				</div>
			</div>
		</div>
	);
};

export default Advanced;
