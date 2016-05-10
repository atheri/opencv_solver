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

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class UploadActivity extends AppCompatActivity {

    private Bitmap bitmap;
    String lineEnd = "\r\n";
    String twoHyphens = "--";
    String boundary = "*****";
    String file_path = "";
    int bytesRead, bytesAvailable, bufferSize;
    byte[] buffer;
    int maxBufferSize = 1*1024*1024;
    String filename = "camera.png";
    int severResponseCode = 0;
    String result;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.upload);

        // Receiving the data from previous activity
        Intent i = getIntent();

        // image or video path that is captured in previous activity
        final String filePath = i.getStringExtra("filePath");
        file_path = filePath;

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
                File sourceFile = new File(file_path);
                FileInputStream fis = new FileInputStream(sourceFile);

                // Setup request
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setDoInput(true);
                conn.setDoOutput(true);
                conn.setUseCaches(false);
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Connection", "Keep-Alive");
                conn.setRequestProperty("ENCTYPE", "multipart/form-data");
                conn.setRequestProperty("Cache-Control", "no-cache");
                conn.setRequestProperty("Content-Type", "multipart/form-data;boundary=" + boundary);
                conn.setRequestProperty("uploaded_file", filename);

                // Start content wrapper
                DataOutputStream dos = new DataOutputStream(conn.getOutputStream());
                dos.writeBytes(twoHyphens + boundary + lineEnd);
                dos.writeBytes("Content-Disposition: form-data; name=\"uploaded_file\";filename=\""+ filename +"\"" + lineEnd);
                dos.writeBytes(lineEnd);

                bytesAvailable = fis.available();

                bufferSize = Math.min(bytesAvailable, maxBufferSize);
                buffer = new byte[bufferSize];

                bytesRead = fis.read(buffer, 0, bufferSize);

                while(bytesRead > 0) {
                    dos.write(buffer, 0, bufferSize);
                    bytesAvailable = fis.available();
                    bufferSize = Math.min(bytesAvailable, maxBufferSize);
                    bytesRead = fis.read(buffer, 0, bufferSize);
                }

                dos.writeBytes(lineEnd);
                dos.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd);

                fis.close();
                dos.flush();
                dos.close();

                severResponseCode = conn.getResponseCode();
                String serverResponseMessage = conn.getResponseMessage();
                Log.e("CJL:", "HTTP Response is: " + serverResponseMessage + ": " + severResponseCode);

                if (severResponseCode == HttpURLConnection.HTTP_OK) {
                    InputStream responseStream = new BufferedInputStream(conn.getInputStream());
                    BufferedReader responseStreamReader = new BufferedReader(new InputStreamReader(responseStream));

                    String line = "";
                    StringBuilder stringBuilder = new StringBuilder();

                    while ((line = responseStreamReader.readLine()) != null) {
                        stringBuilder.append(line).append("\n");
                    }
                    responseStreamReader.close();

                    result = stringBuilder.toString();

                    responseStream.close();

                } else {
                    result =  "Failure"; //TODO Do something else
                }

                conn.disconnect();
                return result;

            } catch (Exception e) {
                this.exception = e;
                return null;
            }
        }

        protected void onPostExecute(String s) {
            //TODO check this.exception
            //TODO do something with the success

            Log.d("CJL:", s);
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

