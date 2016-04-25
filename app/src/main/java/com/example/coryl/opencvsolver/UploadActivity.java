package com.example.coryl.opencvsolver;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import java.io.DataOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.ByteBuffer;

public class UploadActivity extends AppCompatActivity {

    private Bitmap bitmap;
    String attachmentName = "bitmap";
    String attachmentFileName = "bitmap.bmp";
    String lineEnd = "\r\n";
    String twoHyphens = "--";
    String boundary = "*****";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.upload);

        // Receiving the data from previous activity
        Intent i = getIntent();

        // image or video path that is captured in previous activity
        final String filePath = i.getStringExtra("filePath");

        // set imgPreview to image at filePath
        previewImage(filePath);
        bitmap = BitmapFactory.decodeFile(filePath);

        Button btnUpload = (Button) findViewById(R.id.btnUpload);

        assert btnUpload != null;
        btnUpload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new SendBitmap().execute(filePath);
            }
        });
    }

    private class SendBitmap extends AsyncTask<String, Void, String> {

        private Exception exception;

        protected String doInBackground(String... urls) {
            try {
                URL url = new URL(Config.FILE_UPLOAD_URL);

                // Setup request
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setDoInput(true);
                connection.setDoOutput(true);
                connection.setUseCaches(false);
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Connection", "Keep-Alive");
                connection.setRequestProperty("Cache-Control", "no-cache");
                connection.setRequestProperty("Content-Type", "multipart/form-data;boundary=" + boundary);

                // Start content wrapper
                DataOutputStream request = new DataOutputStream(connection.getOutputStream());
                request.writeBytes(twoHyphens + boundary + lineEnd);
                request.writeBytes("Content-Disposition: form-data; name=\"" +
                        attachmentName + "\";filename=\"" +
                        attachmentFileName + "\"" + lineEnd);
                request.writeBytes(lineEnd);

                // Covert bitmap to ByteBuffer
                int bytes = bitmap.getByteCount();
                ByteBuffer buffer = ByteBuffer.allocate(bytes);
                bitmap.copyPixelsToBuffer(buffer);
                byte[] pixels = buffer.array();

                request.write(pixels);

                // End content wrapper
                request.writeBytes(lineEnd);
                request.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd);

                // flush output buffer
                request.flush();
                request.close();

                if (connection.getResponseCode() == HttpURLConnection.HTTP_OK) {
                    return "Success"; //TODO do something else
                } else {
                    return "Failure"; //TODO Do something else
                }
            } catch (Exception e) {
                this.exception = e;
                return null;
            }
        }

        protected void onPostExecute(String s) {
            //TODO check this.exception
            //TODO do something with the success
            Log.d("CJL:", "HTTP STATUS: " + s);
        }
    }



    private void previewImage(String filePath) {
        ImageView imgPreview = (ImageView) findViewById(R.id.imgPreview);
        BitmapFactory.Options options = new BitmapFactory.Options();
        options.inSampleSize = 4; // down sample image (out of memory otherwise)
        final Bitmap previewBitmap = BitmapFactory.decodeFile(filePath, options);
        assert imgPreview != null;
        imgPreview.setImageBitmap(previewBitmap);
    }
}

