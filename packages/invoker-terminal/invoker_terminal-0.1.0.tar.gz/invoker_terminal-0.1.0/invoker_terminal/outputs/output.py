import io
import zipfile


class InvokerOutput:
    outputs = []
    fileCounter = 0

    def addText(content: str, filename=None):
        if filename:
            InvokerOutput.outputs.append(
                (filename, io.BytesIO(content.encode("utf-8")))
            )
        else:
            InvokerOutput.outputs.append(
                (
                    str(InvokerOutput.fileCounter),
                    io.BytesIO(content.encode("utf-8")),
                )
            )
            InvokerOutput.fileCounter += 1

    def done():
        zip_buffer = io.BytesIO()
        print(InvokerOutput.outputs)
        with zipfile.ZipFile(
            zip_buffer, "a", zipfile.ZIP_DEFLATED, False
        ) as zip_file:
            for file_name, data in InvokerOutput.outputs:
                zip_file.writestr(
                    "output/{}".format(file_name), data.getvalue()
                )

        with open("/invoker/output.zip", "wb") as f:
            f.write(zip_buffer.getvalue())
