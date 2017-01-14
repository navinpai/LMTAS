package lmtas.app.com.lmtas;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private String imageBase64;
    private String mCurrentPhotoPath;
    private ImageView mImageView;
    private String amount;
    private String serverResp = "{\"message\": \"Random Error\", \"success\": false}";

    private static String URL = "http://ec2-52-207-219-42.compute-1.amazonaws.com:1337/upload";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button btnClick, btnUpload, btnGallery;
        mImageView = (ImageView) findViewById(R.id.Imageprev);

        /*btnClick = (Button) findViewById(R.id.cpic);


        btnClick.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                captureImage();
            }
        });
        */

        FloatingActionButton lfab = (FloatingActionButton) findViewById(R.id.lfab);
        lfab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
               captureImage();
            }
        });

        FloatingActionButton rfab = (FloatingActionButton) findViewById(R.id.rfab);
        rfab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                selectImage();
            }
        });

        btnUpload = (Button) findViewById(R.id.up);
        btnUpload.setVisibility(View.INVISIBLE);

        btnUpload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                upload();
            }
        });

        /*btnGallery = (Button) findViewById(R.id.gallery);
        btnGallery.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                selectImage();
            }
        });
        */
    }

    private void upload() {
        Bitmap bm = BitmapFactory.decodeFile(mCurrentPhotoPath);
        ByteArrayOutputStream bao = new ByteArrayOutputStream();
        bm.compress(Bitmap.CompressFormat.JPEG, 50, bao);
        byte[] ba = bao.toByteArray();
        imageBase64 = Base64.encodeToString(ba, Base64.DEFAULT);

        // Upload image to server
        new uploadToServer().execute();

    }

    private void captureImage() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        // Ensure that there's a camera activity to handle the intent
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            // Create the File where the photo should go
            File photoFile = null;
            try {
                photoFile = createImageFile();
            } catch (IOException ex) {
                // Error occurred while creating the File
                ex.printStackTrace();
            }
            // Continue only if the File was successfully created
            if (photoFile != null) {
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT,
                        Uri.fromFile(photoFile));
                startActivityForResult(takePictureIntent, 100);
            }
        }
    }

    private void selectImage() {
        Intent intent = new Intent(Intent.ACTION_GET_CONTENT, android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(Intent.createChooser(intent, "Select Picture"), 200);
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == 100 && resultCode == RESULT_OK) {
            setPicFromCamera();
        }
        else if (requestCode == 200 && resultCode == RESULT_OK) {
            Uri selectedImage = data.getData();
            mCurrentPhotoPath = getRealPathFromURI(selectedImage);
            Bitmap bitmap = null;
            try {
                bitmap = MediaStore.Images.Media.getBitmap(this.getContentResolver(), selectedImage);
            } catch (IOException e) {
                e.printStackTrace();
            }
            setPicFromGallery(bitmap);
        }
    }

    public String getRealPathFromURI(Uri uri) {
        String[] projection = { MediaStore.Images.Media.DATA };
        @SuppressWarnings("deprecation")
        Cursor cursor = managedQuery(uri, projection, null, null, null);
        int column_index = cursor
                .getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
        cursor.moveToFirst();
        return cursor.getString(column_index);
    }

    public class uploadToServer extends AsyncTask<Void, Void, String> {

        private ProgressDialog progresssDialog = new ProgressDialog(MainActivity.this);

        protected void onPreExecute() {
            super.onPreExecute();
            EditText mEdit   = (EditText)findViewById(R.id.amount);
            amount = mEdit.getText().toString();
            progresssDialog.setMessage("Uploading your selfie!");
            progresssDialog.show();
        }

        @Override
        protected String doInBackground(Void... params) {

            ArrayList<NameValuePair> nameValuePairs = new ArrayList<>();
            nameValuePairs.add(new BasicNameValuePair("file", imageBase64));
            nameValuePairs.add(new BasicNameValuePair("amount", amount));
            nameValuePairs.add(new BasicNameValuePair("userName", "navin"));
            try {
                HttpClient httpclient = new DefaultHttpClient();
                HttpPost httppost = new HttpPost(URL);
                httppost.setEntity(new UrlEncodedFormEntity(nameValuePairs));
                HttpResponse response = httpclient.execute(httppost);
                serverResp = EntityUtils.toString(response.getEntity());
                Log.v("log_tag", "In the try Loop" + serverResp);

            } catch (Exception e) {
                Log.v("log_tag", "Error in http connection " + e.toString());
            }

            return "Success";

        }

        protected void onPostExecute(String result) {
            super.onPostExecute(result);
            Context context = getApplicationContext();
            JSONObject jObj;
            CharSequence text = "";
            try {
                jObj = new JSONObject(serverResp);
                text = jObj.getString("message");
                int duration = Toast.LENGTH_LONG;
                Toast toast = Toast.makeText(context, text, duration);
                toast.show();
                if (jObj.getBoolean("success")){
                    Intent myIntent = new Intent(MainActivity.this,
                            HomeActivity.class);
                    myIntent.setFlags(1);
                    startActivity(myIntent);
                }

            } catch (JSONException e) {
                e.printStackTrace();
            }


            progresssDialog.hide();
            progresssDialog.dismiss();
        }
    }

    private void setPicFromCamera() {
        // Get the dimensions of the View
        int targetW = mImageView.getWidth();
        int targetH = mImageView.getHeight();

        // Get the dimensions of the bitmap
        BitmapFactory.Options bmOptions = new BitmapFactory.Options();
        bmOptions.inJustDecodeBounds = true;
        BitmapFactory.decodeFile(mCurrentPhotoPath, bmOptions);
        int photoW = bmOptions.outWidth;
        int photoH = bmOptions.outHeight;

        // Determine how much to scale down the image
        int scaleFactor = Math.min(photoW / targetW, photoH / targetH);

        // Decode the image file into a Bitmap sized to fill the View
        bmOptions.inJustDecodeBounds = false;
        bmOptions.inSampleSize = scaleFactor;
        bmOptions.inPurgeable = true;

        Bitmap bitmap = BitmapFactory.decodeFile(mCurrentPhotoPath, bmOptions);
        mImageView.setImageBitmap(bitmap);
    }

    private void setPicFromGallery(Bitmap bitmap) {
        // Get the dimensions of the View
        int targetW = mImageView.getWidth();
        int targetH = mImageView.getHeight();

        // Get the dimensions of the bitmap
        int photoW = bitmap.getWidth();
        int photoH = bitmap.getHeight();

        // Determine how much to scale down the image
        int scaleFactor = Math.min(photoW / targetW, photoH / targetH);

        // Decode the image file into a Bitmap sized to fill the View
        //bmOptions.inJustDecodeBounds = false;
        //bitmap.setSc.inSampleSize = scaleFactor;
        //bmOptions.inPurgeable = true;

        //Bitmap bitmap2 = BitmapFactory.decodeFile(mCurrentPhotoPath, bmOptions);
        mImageView.setImageBitmap(bitmap);
        Button btnUpload = (Button) findViewById(R.id.up);
        btnUpload.setVisibility(View.VISIBLE);
    }

    private File createImageFile() throws IOException {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.ENGLISH).format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_PICTURES);

        File image = File.createTempFile(
                imageFileName,  /* prefix */
                ".jpg",         /* suffix */
                storageDir      /* directory */
        );

        // Save a file: path for use with ACTION_VIEW intents
        mCurrentPhotoPath = image.getAbsolutePath();
        Log.e("Getpath", "Cool" + mCurrentPhotoPath);
        return image;
    }


}
