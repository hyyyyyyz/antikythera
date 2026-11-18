"""Small, synchronized native SVG tracks. All times are integer milliseconds."""


def number(value):
    return f"{value:.5f}".rstrip("0").rstrip(".") or "0"


def xy(point):
    return " ".join(number(n) for n in point)


def track(duration, attribute, keys, *, mode="discrete", transform=None):
    keys = list(keys)
    if not duration or len({v for _, v in keys}) < 2:
        return ""
    if keys[0][0]:
        keys.insert(0, (0, keys[0][1]))
    if keys[-1][0] != duration:
        keys.append((duration, keys[-1][1]))
    times = ";".join(f"{ms/duration:.7f}".rstrip("0").rstrip(".") for ms, _ in keys)
    values = ";".join(str(v) for _, v in keys)
    tag = "animateTransform" if transform else "animate"
    kind = f' type="{transform}"' if transform else ""
    return (
        f'<{tag} attributeName="{attribute}"{kind} dur="{duration}ms" repeatCount="indefinite" '
        f'calcMode="{mode}" keyTimes="{times}" values="{values}"/>'
    )


def frames_track(frames, attribute, value, *, mode="discrete", transform=None):
    values = [value(f) for f in frames]
    keys = [(frames[0].ms, values[0])]
    for i in range(1, len(frames) - 1):
        if values[i] != values[i - 1] or (
            mode == "linear" and values[i] != values[i + 1]
        ):
            keys.append((frames[i].ms, values[i]))
    if len(frames) > 1:
        keys.append((frames[-1].ms, values[-1]))
    return track(frames[-1].ms, attribute, keys, mode=mode, transform=transform)
