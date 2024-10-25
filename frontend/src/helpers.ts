// Types

export interface PyResponse {
	type: "ok" | "err";
	data: string;
}

export type PyFileType = "encoder" | "decoder" | "tokenizer";

declare global {
	interface Window {
		pywebview: {
			api: {
				infer: (image_data: string) => Promise<PyResponse>;
				init_pipeline: () => Promise<PyResponse>;
				destroy_pipeline: () => Promise<PyResponse>;
				open_image: () => Promise<PyResponse>;
				import_file: (file_type: PyFileType) => Promise<PyResponse>;
				remove_file: (file_type: PyFileType) => Promise<PyResponse>;
				download_missing_model_from_hf: () => Promise<PyResponse>;
				get_file_status: () => Promise<{
					encoder: boolean;
					decoder: boolean;
					tokenizer: boolean;
				}>;
				minimize: () => Promise<void>;
				quit: () => Promise<void>;
			};
		};
	}
}

// Functions

export const nameToFileType = (
	name: "Encoder Model" | "Decoder Model" | "Tokenizer",
): PyFileType => {
	switch (name) {
		case "Encoder Model":
			return "encoder";
		case "Decoder Model":
			return "decoder";
		case "Tokenizer":
			return "tokenizer";
	}
};
