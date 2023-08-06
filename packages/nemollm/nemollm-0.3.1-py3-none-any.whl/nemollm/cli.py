import argparse
import json

from nemollm.api import NemoLLM


def generate_cli(args):
    nemollm = NemoLLM()

    if args.stop is not None:
        args.stop = args.stop.replace('\\n', '\n').replace('\\t', '\t')
        args.stop = args.stop.split(',')
    # escape \n and \t since cli automatically converts \n into \\n
    args.prompt = args.prompt.replace('\\n', '\n').replace('\\t', '\t')
    response = nemollm.generate(
        model=args.model,
        prompt=args.prompt,
        customization_id=args.customization_id,
        return_type=args.return_type,
        tokens_to_generate=args.tokens_to_generate,
        logprobs=args.logprobs,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        stop=args.stop,
        random_seed=args.random_seed,
        repetition_penalty=args.repetition_penalty,
        beam_search_diversity_rate=args.beam_search_diversity_rate,
        beam_width=args.beam_width,
        length_penalty=args.length_penalty,
        disable_logging=args.disable_logging,
    )

    if args.return_type == 'text':
        print(response)
    elif args.return_type == 'json':
        print(json.dumps(response, indent=4))
    elif args.return_type == 'stream':
        for line in response:
            # there might be some empty lines to maintain connection
            if line:
                datapoint = json.loads(line)
                # disable flush if prefer to update terminal every sentence instead of every token
                if 'text' in datapoint:
                    print(datapoint['text'], sep='', end='', flush=True)


def add_generate_parser(subparsers):
    generate_api = subparsers.add_parser("generate")
    generate_api.add_argument("-p", "--prompt", required=True)
    generate_api.add_argument("-m", "--model", required=True)
    generate_api.add_argument("-cid", "--customization_id")
    generate_api.add_argument("-n", "--tokens_to_generate", type=int)
    generate_api.add_argument("-rt", "--return_type", default="json", choices=['json', 'text', 'stream'])
    generate_api.add_argument("--logprobs", action="store_true")
    generate_api.add_argument("-t", "--temperature", type=float)
    generate_api.add_argument("--top_p", type=float)
    generate_api.add_argument("--top_k", type=int)
    generate_api.add_argument(
        '--stop',
        help="Please enter a list of separators joined using commas without space, if escaped chars (newline, tab) need to be used, please enter \\n or \\t instead of \n or \t",
    )
    generate_api.add_argument("--random_seed", type=int)
    generate_api.add_argument("--repetition_penalty", type=float)
    generate_api.add_argument("--beam_search_diversity_rate", type=float)
    generate_api.add_argument("--beam_width", type=int)
    generate_api.add_argument("--length_penalty", type=float)
    generate_api.add_argument("--disable_logging", action="store_true")
    generate_api.set_defaults(func=generate_cli)


def upload_cli(args):
    nemollm = NemoLLM()
    response = nemollm.upload(args.filename, progress_bar=args.progress_bar)
    print(response)


def add_upload_parser(subparsers):
    upload_api = subparsers.add_parser("upload")
    upload_api.add_argument("-f", "--filename", required=True)
    upload_api.add_argument("-tqdm", "--progress_bar", action="store_true")
    upload_api.set_defaults(func=upload_cli)


def create_customization_cli(args):
    nemollm = NemoLLM()
    response = nemollm.create_customization(
        model=args.model,
        training_dataset_file_id=args.training_dataset_file_id,
        name=args.name,
        validation_dataset_file_id=args.validation_dataset_file_id,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        num_virtual_tokens=args.num_virtual_tokens,
    )
    print(json.dumps(response, indent=4))


def add_create_customization_parser(subparsers):
    create_customization_api = subparsers.add_parser("create_customization")
    create_customization_api.add_argument("-m", "--model", required=True)
    create_customization_api.add_argument("-t", "--training_dataset_file_id", required=True)
    create_customization_api.add_argument("--name", required=True)
    create_customization_api.add_argument("-v", "--validation_dataset_file_id")
    create_customization_api.add_argument("-e", "--epochs", type=int)
    create_customization_api.add_argument("-bs", "--batch_size", type=int)
    create_customization_api.add_argument("-lr", "--learning_rate", type=float)
    create_customization_api.add_argument("-nvt", "--num_virtual_tokens", type=int)
    create_customization_api.set_defaults(func=create_customization_cli)


def list_customizations_cli(args):
    nemollm = NemoLLM()
    response = nemollm.list_customizations(
        page=args.page, page_size=args.page_size, shared=args.shared, sort_by=args.sort_by, order=args.order
    )
    print(json.dumps(response, indent=4))


def add_list_customizations_parser(subparsers):
    list_customizations_api = subparsers.add_parser("list_customizations")
    list_customizations_api.add_argument("-p", "--page", type=int)
    list_customizations_api.add_argument("-ps", "--page_size", type=int)
    list_customizations_api.add_argument("-s", "--shared")
    list_customizations_api.add_argument("-sb", "--sort_by")
    list_customizations_api.add_argument("-o", "--order")
    list_customizations_api.set_defaults(func=list_customizations_cli)


def list_models_cli(args):
    nemollm = NemoLLM()
    response = nemollm.list_models()
    print(json.dumps(response, indent=4))


def add_list_models_parser(subparsers):
    list_models_api = subparsers.add_parser("list_models")
    list_models_api.set_defaults(func=list_models_cli)


def list_files_cli(args):
    nemollm = NemoLLM()
    response = nemollm.list_files()
    print(json.dumps(response, indent=4))


def add_list_files_parser(subparsers):
    list_files_api = subparsers.add_parser("list_files")
    list_files_api.set_defaults(func=list_files_cli)


def delete_file_cli(args):
    nemollm = NemoLLM()
    response = nemollm.delete_file(args.file_id)
    print(response)


def add_delete_file_parser(subparsers):
    delete_file_api = subparsers.add_parser("delete_file")
    delete_file_api.add_argument("-f", "--file_id", required=True)
    delete_file_api.set_defaults(func=delete_file_cli)


def get_info_file_cli(args):
    nemollm = NemoLLM()
    response = nemollm.get_info_file(args.file_id)
    print(json.dumps(response, indent=4))


def add_get_info_file_parser(subparsers):
    get_info_customization_api = subparsers.add_parser("get_info_file")
    get_info_customization_api.add_argument("-fid", "--file_id", required=True)
    get_info_customization_api.set_defaults(func=get_info_file_cli)


def get_info_customization_cli(args):
    nemollm = NemoLLM()
    response = nemollm.get_info_customization(args.model, args.customization_id)
    print(json.dumps(response, indent=4))


def add_get_info_customization_parser(subparsers):
    get_info_customization_api = subparsers.add_parser("get_info_customization")
    get_info_customization_api.add_argument("-m", "--model", required=True)
    get_info_customization_api.add_argument("-cid", "--customization_id", required=True)
    get_info_customization_api.set_defaults(func=get_info_customization_cli)


def get_customization_training_metrics_cli(args):
    nemollm = NemoLLM()
    response = nemollm.get_customization_training_metrics(args.model, args.customization_id)
    print(json.dumps(response, indent=4))


def add_get_customization_training_metrics_parser(subparsers):
    get_info_customization_api = subparsers.add_parser("get_customization_training_metrics")
    get_info_customization_api.add_argument("-m", "--model", required=True)
    get_info_customization_api.add_argument("-cid", "--customization_id", required=True)
    get_info_customization_api.set_defaults(func=get_customization_training_metrics_cli)


def delete_customization_cli(args):
    nemollm = NemoLLM()
    response = nemollm.delete_customization(args.model, args.customization_id)
    print(response)


def add_delete_customization_parser(subparsers):
    delete_customization_api = subparsers.add_parser("delete_customization")
    delete_customization_api.add_argument("-m", "--model", required=True)
    delete_customization_api.add_argument("-cid", "--customization_id", required=True)
    delete_customization_api.set_defaults(func=delete_customization_cli)


def download_customization_cli(args):
    nemollm = NemoLLM()
    response = nemollm.download_customization(args.model, args.customization_id, args.save_filename)
    print(response)


def add_download_customization_parser(subparsers):
    download_customization_api = subparsers.add_parser("download_customization")
    download_customization_api.add_argument("-m", "--model", required=True)
    download_customization_api.add_argument("-cid", "--customization_id", required=True)
    download_customization_api.add_argument("-f", "--save_filename", required=True)
    download_customization_api.set_defaults(func=download_customization_cli)


def main():
    parser = argparse.ArgumentParser(description=None)
    subparsers = parser.add_subparsers()

    add_generate_parser(subparsers)
    add_upload_parser(subparsers)
    add_create_customization_parser(subparsers)
    add_list_customizations_parser(subparsers)
    add_list_models_parser(subparsers)
    add_list_files_parser(subparsers)
    add_delete_file_parser(subparsers)
    add_delete_customization_parser(subparsers)
    add_get_info_customization_parser(subparsers)
    add_get_info_file_parser(subparsers)
    add_download_customization_parser(subparsers)
    add_get_customization_training_metrics_parser(subparsers)

    args = parser.parse_args()
    print(args)
    args.func(args)
