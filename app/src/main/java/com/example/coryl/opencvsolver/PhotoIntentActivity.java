package com.example.coryl.opencvsolver;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class PhotoIntentActivity extends AppCompatActivity {

    private static final int CAPTURE_IMAGE_ACTIVITY_REQUEST_CODE = 100;
    private Uri fileUri;
    private ImageView mImageView;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        this.mImageView = (ImageView) this.findViewById(R.id.imageView1);
        Button photoButton = (Button) this.findViewById(R.id.button1);
        assert photoButton != null;
        photoButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent cameraIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                fileUri = getOutputMediaFileUri();
                cameraIntent.putExtra(MediaStore.EXTRA_OUTPUT, fileUri);
                startActivityForResult(cameraIntent, CAPTURE_IMAGE_ACTIVITY_REQUEST_CODE);
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == CAPTURE_IMAGE_ACTIVITY_REQUEST_CODE ) {
            if (resultCode == RESULT_OK) {
                Toast.makeText(this, "is null", Toast.LENGTH_LONG).show();
                DisplayMetrics metrics = new DisplayMetrics();
                getWindowManager().getDefaultDisplay().getMetrics(metrics);
                try {
                    Bitmap orig = MediaStore.Images.Media.getBitmap(getContentResolver(), fileUri);
                    int width = orig.getWidth();
                    int height = orig.getHeight();
                    double scale = 1;
                    if (width > 4096 || height > 4096) {
                        if (width > height) {
                            scale = 4096/(double)width;
                        } else {
                            scale = 4096/(double)height;
                        }
                    }
                    width = (int)(width*scale);
                    height = (int)(height*scale);

                    Bitmap photo = Bitmap.createScaledBitmap(orig, width, height, true);
                    mImageView.setImageBitmap(photo);
                } catch (IOException e) {
                    Log.e(getString(R.string.app_name), "exception", e);
                }
            } else if (resultCode == RESULT_CANCELED) {
                //TODO//user cancelled the image capture
            } else {
                //TODO//image capture failed, do something
            }
        }
    }

    /** Create a file Uri for saving an image or video */
    private Uri getOutputMediaFileUri(){
        return Uri.fromFile(getOutputMediaFile());
    }

    /** Create a File for saving an image or video */
    private File getOutputMediaFile() {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_PICTURES);

        File image = null;
        try {
            image = File.createTempFile(
                    imageFileName,  /* prefix */
                    ".jpg",         /* suffix */
                    storageDir      /* directory */
            );
        } catch (IOException e) {
            Log.e(getString(R.string.app_name), "exception", e);
        }
        return image;
    }
}
