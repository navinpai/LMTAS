package lmtas.app.com.lmtas;

import android.app.ProgressDialog;
import android.graphics.Typeface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class HomeActivity extends AppCompatActivity {

    private static String URL = "http://ec2-52-207-219-42.compute-1.amazonaws.com:1337/getDetails";
    private List<String> your_array_list;
    private ArrayAdapter<String> arrayAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().hide();

        TextView tv = (TextView) findViewById(R.id.titleText);
        Typeface prisma = Typeface.createFromAsset(getAssets(), "fonts/Prisma.ttf");
        tv.setTypeface(prisma);

        ListView lv;
        lv = (ListView) findViewById(R.id.tList);

        new getDetails().execute();

        your_array_list = new ArrayList<String>();
        your_array_list.add("foo");
        your_array_list.add("bar");
        your_array_list.add("camp");

        arrayAdapter = new ArrayAdapter<String>(
                this,
                android.R.layout.simple_list_item_1,
                your_array_list);

        lv.setAdapter(arrayAdapter);


        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });

        FloatingActionButton lfab = (FloatingActionButton) findViewById(R.id.lfab);
        lfab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Left Action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });

    }

    public class getDetails extends AsyncTask<Void, Void, String> {

        private ProgressDialog progresssDialog = new ProgressDialog(HomeActivity.this);

        protected void onPreExecute() {
            super.onPreExecute();
            progresssDialog.setMessage("Getting data");
            progresssDialog.show();
        }

        @Override
        protected String doInBackground(Void... params) {

            try {
                HttpClient httpclient = new DefaultHttpClient();
                HttpGet httpget = new HttpGet(URL);
                HttpResponse response = httpclient.execute(httpget);
                String st = EntityUtils.toString(response.getEntity());
                JSONObject jObj = new JSONObject(st);

                JSONArray transactions = (JSONArray) jObj.get("lastTransactions");

                if (transactions != null) {
                    for (int i=0;i<transactions.length();i++) {
                        your_array_list.add(transactions.getString(i));
                    }
                }
                arrayAdapter.notifyDataSetChanged();
                Log.v("log_tag", "In the try Loop" + st);

            } catch (Exception e) {
                Log.v("log_tag", "Error in http connection " + e.toString());
            }

            return "Success";

        }

        protected void onPostExecute(String result) {
            super.onPostExecute(result);
            progresssDialog.hide();
            progresssDialog.dismiss();
        }
    }

}
