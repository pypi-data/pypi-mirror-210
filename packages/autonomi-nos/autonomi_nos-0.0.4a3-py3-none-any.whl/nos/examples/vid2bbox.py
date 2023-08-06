

@serve_grpc_cli.async_command("vid2bbox", help="Predict bounding boxes from videos.")
async def _predict_vid2bbox(
    ctx: typer.Context,
    model_name: str = typer.Option(
        "yolox/small",
        "-m",
        "--model-name",
        help="Name of the model to use (e.g. yolox/small).",
    ),
    filename: str = typer.Option(..., "-i", "--input", help="Input video filename."),
    batch_size: int = typer.Option(128, "-b", "--batch-size", help="Batch size."),
) -> None:
    from itertools import islice

    import av

    def video_iterator(filename: str, chunk_size: int):
        """Simple video iterator with chunked reads."""
        if not Path(filename).exists():
            raise FileNotFoundError(f"Video not found (filename={filename}).")

        video = av.open(open(filename, "rb"))
        frames = video.decode(video=0)
        while batch := tuple(islice(frames, chunk_size)):
            yield [np.asarray(frame.to_image()) for frame in batch]

    def video_iterator_bytes(filename: str, chunk_size: int):
        """Simple video iterator with chunked reads."""
        if not Path(filename).exists():
            raise FileNotFoundError(f"Video not found (filename={filename}).")

        video = av.open(open(filename, "rb"))
        for packet in video.demux():
            yield packet.to_bytes()

    # Client-side batching
    tbytes, tbytes_im = 0, 0
    for bytes in tqdm(video_iterator_bytes(filename, 1)):
        tbytes += len(bytes)
    for img in tqdm(video_iterator(filename, 1)):
        tbytes_im += img[0].nbytes
    print(f"Total bytes: {tbytes}, Total bytes (img): {tbytes_im}")
    import pdb; pdb.set_trace()


    options = [
        ("grpc.max_message_length", 512 * 1024 * 1024),
        ("grpc.max_send_message_length", 512 * 1024 * 1024),
        ("grpc.max_receive_message_length", 512 * 1024 * 1024),
    ]

    with rich.status.Status("[bold green] Predict bounding boxes ...[/bold green]"):
        async with grpc.aio.insecure_channel(ctx.obj.address, options=options) as channel:
            stub = nos_service_pb2_grpc.InferenceServiceStub(channel)
            st = time.perf_counter()
            try:
                nboxes, nframes = 0, 0
                for idx, img in tqdm(enumerate(video_iterator(filename, batch_size)), disable=True):
                    response = await stub.Predict(
                        nos_service_pb2.InferenceRequest(
                            method="img2bbox",
                            model_name=model_name,
                            image_request=nos_service_pb2.ImageRequest(image_bytes=ray.cloudpickle.dumps(img)),
                        )
                    )
                    response = ray.cloudpickle.loads(response.result)
                    _scores, _labels, bboxes = response["bboxes"], response["scores"], response["labels"]
                    nboxes += sum([len(bbox) for bbox in bboxes])
                    nframes += len(bboxes)
                runtime = time.perf_counter() - st
                fps = nframes / runtime
                console.print(
                    f"[bold green] ✓ Predicted bounding boxes (frames={nframes}, nboxes={nboxes}, [/bold green][bold yellow]time=~{runtime * 1e3:.1f}ms, fps={fps:.1f}[/bold yellow][bold green])[/bold green]"
                )
            except grpc.RpcError as e:
                console.print(f"[red] ✗ Failed to predict bounding boxes (text={e}).[/red]")
                return
