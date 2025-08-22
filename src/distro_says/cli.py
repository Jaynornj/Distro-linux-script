import click
from .core import (
    resolve_data_dirs, load_all_distros, detect_distro,
    normalize_key, load_ascii, pick_message
)
from .render import print_ascii, print_summary


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--data-dir", metavar="PATH",
              help="Directory with quotes/ and images/ (or set DISTRO_SAYS_DIR).")
@click.pass_context
def main(ctx: click.Context, data_dir: str | None):
    """What your Linux distro says about you (data-driven)."""
    ctx.ensure_object(dict)
    ctx.obj["data_dir"] = data_dir


@main.command("list")
@click.pass_context
def list_cmd(ctx: click.Context):
    """List available distro keys (from quotes/*.json)."""
    quotes_dir, _ = resolve_data_dirs(ctx.obj.get("data_dir"))
    distros = load_all_distros(quotes_dir)
    if not distros:
        click.echo("(no distros found — add JSON files to quotes/)", err=True)
        raise SystemExit(1)
    for key in sorted(distros.keys()):
        click.echo(key)


@main.command("show")
@click.argument("distro", required=False)
@click.option("--auto", is_flag=True, help="Detect distro from /etc/os-release.")
@click.option("--ascii/--no-ascii", "show_ascii", default=True,
              help="Show ASCII logo from images/<key>.txt.")
@click.option("--json", "json_mode", is_flag=True, help="Output JSON.")
@click.pass_context
def show_cmd(ctx: click.Context, distro: str | None, auto: bool,
             show_ascii: bool, json_mode: bool):
    """Show what the chosen distro says about you."""
    quotes_dir, images_dir = resolve_data_dirs(ctx.obj.get("data_dir"))
    distros = load_all_distros(quotes_dir)

    key = None
    if auto:
        key = detect_distro()
    key = distro or key
    if not key:
        raise click.UsageError("Provide DISTRO or use --auto")

    norm = normalize_key(key, distros)
    if not norm:
        raise click.UsageError(f"Unknown distro '{key}'. Try: distro-says list")

    bundle = distros[norm]
    ascii_art = load_ascii(images_dir, norm) if show_ascii else None
    message = pick_message(bundle)

    print_ascii(ascii_art)
    print_summary(bundle.get("name", norm.title()),
                  bundle.get("tagline", ""),
                  message,
                  json_mode=json_mode)


@main.command("random")
@click.option("--ascii/--no-ascii", "show_ascii", default=True)
@click.pass_context
def random_cmd(ctx: click.Context, show_ascii: bool):
    """Pick a random distro and show its message."""
    import random
    quotes_dir, images_dir = resolve_data_dirs(ctx.obj.get("data_dir"))
    distros = load_all_distros(quotes_dir)
    if not distros:
        click.echo("No distros available. Add JSON files to quotes/ first.", err=True)
        raise SystemExit(1)

    key = random.choice(sorted(distros.keys()))
    bundle = distros[key]
    ascii_art = load_ascii(images_dir, key) if show_ascii else None
    message = pick_message(bundle)

    print_ascii(ascii_art)
    print_summary(bundle.get("name", key.title()),
                  bundle.get("tagline", ""),
                  message,
                  json_mode=False)
