import asyncio
from argparse import ArgumentParser

from ptpython.repl import embed

from bovine import BovineClient


def build_parser():
    parser = ArgumentParser("Opens a REPL with preloaded BovineClient client")
    parser.add_argument("--domain", help="Domain the actor can be found on")
    parser.add_argument("--secret", help="Secret associated with the account")
    parser.add_argument("--config_file", help="Toml fail containing domain and secret")

    return parser


def config(repl):
    repl.use_code_colorscheme("dracula")
    repl.enable_output_formatting = True


async def repl(client):
    async with client:
        activity_factory, object_factory = client.factories
        print("The variable client contains your BovineClient")
        print("The variables activity_factory and object_factory")
        print("contain the corresponding objects")
        print("With await client.inbox() and await client.outbox()")
        print("one can interface with these two")
        await embed(
            globals=globals(),
            locals=locals(),
            return_asyncio_coroutine=True,
            patch_stdout=True,
            configure=config,
        )


def main():
    args = build_parser().parse_args()

    if args.config_file:
        client = BovineClient.from_file(args.config_file)
    elif args.domain and args.secret:
        client = BovineClient({"host": args.domain, "private_key": args.secret})
    else:
        print("Please specify either domain and secret or a configuration file")
        exit(1)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(repl(client))


if __name__ == "__main__":
    main()
