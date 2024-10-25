import { useStore } from "@nanostores/solid";
import type { JSXElement } from "solid-js";

import { FileStatus } from "./fileStatus";

import {
	$isDecoderExist,
	$isEncoderExist,
	$isTokenizerExist,
} from "../../stores/states";

const ModelMgr = (): JSXElement => {
	const isEncoderExist = useStore($isEncoderExist);
	const isDecoderExist = useStore($isDecoderExist);
	const isTokenizerExist = useStore($isTokenizerExist);

	return (
		<div>
			<div class="font-medium text-sm mb-2 ml-3 text-gray-600">
				Model Management
			</div>
			<div class="flex flex-col justify-between px-2 bg-gray-100 rounded-lg mb-3">
				<div class="border-b border-gray-300">
					<FileStatus
						name="Encoder Model"
						icon="simple-icons:onnx"
						isImported={isEncoderExist}
					/>
				</div>
				<div class="border-b border-gray-300">
					<FileStatus
						name="Decoder Model"
						icon="simple-icons:onnx"
						isImported={isDecoderExist}
					/>
				</div>
				<FileStatus
					name="Tokenizer"
					icon="vscode-icons:file-type-json-official"
					isImported={isTokenizerExist}
				/>
			</div>
		</div>
	);
};

export default ModelMgr;
