package lmtas.app.com.lmtas;

import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.messaging.FirebaseMessaging;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class HomeActivity extends AppCompatActivity {

    private static String URL = "http://ec2-52-207-219-42.compute-1.amazonaws.com:1337/getDetails";
    private List<String> txnsList;
    private List<String> balList;
    private ArrayAdapter<String> arrayAdapter;
    private ArrayAdapter<String> barrayAdapter;
    private TextView total;
    private Double totalDbl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        FirebaseMessaging.getInstance().subscribeToTopic("updates");
        new getDetails().execute();
        setContentView(R.layout.activity_home);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().hide();

        TextView tv = (TextView) findViewById(R.id.titleText);
        tv.setTextColor(Color.argb(100, 255, 64, 129));
        Typeface prisma = Typeface.createFromAsset(getAssets(), "fonts/Prisma.ttf");
        tv.setTypeface(prisma);


        ListView lv;
        lv = (ListView) findViewById(R.id.tList);

        ListView blv;
        blv = (ListView) findViewById(R.id.bList);

        txnsList = new ArrayList<String>();
        balList = new ArrayList<String>();

        arrayAdapter = new ArrayAdapter<String>(
                this,
                android.R.layout.simple_list_item_1,
                txnsList);

        barrayAdapter = new ArrayAdapter<String>(
                this,
                android.R.layout.simple_list_item_1,
                balList);

        lv.setAdapter(arrayAdapter);
        //blv.setAdapter(barrayAdapter);


        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent myIntent = new Intent(HomeActivity.this,
                        MainActivity.class);
                myIntent.setFlags(1);
                startActivity(myIntent);
               // Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
               //         .setAction("Action", null).show();
            }
        });

        /* FloatingActionButton lfab = (FloatingActionButton) findViewById(R.id.lfab);
        lfab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent myIntent = new Intent(HomeActivity.this,
                        MainActivity.class);
                myIntent.setFlags(0);
                startActivity(myIntent);
                //Snackbar.make(view, "Left Action", Snackbar.LENGTH_LONG)
                //        .setAction("Action", null).show();
            }
        });
        */

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
                        txnsList.add(transactions.getJSONObject(i).getString("txnPT"));
                    }
                }

                JSONObject balances = (JSONObject) jObj.get("balances");

                if (balances != null) {
                    Iterator<?> keys = balances.keys();
                    while( keys.hasNext() ) {
                        String key = (String)keys.next();
                        balList.add(key + " : Rs. " + balances.get(key).toString());
                    }
                }


                totalDbl = (Double) jObj.get("total");

               // barrayAdapter.notifyDataSetChanged();


                Log.v("log_tag", "In the try Loop" + st);

            } catch (Exception e) {
                Log.v("log_tag", "Error in http connection " + e.toString());
            }

            return "Success";

        }

        protected void onPostExecute(String result) {
            super.onPostExecute(result);
            arrayAdapter.notifyDataSetChanged();
            TextView tv = (TextView) findViewById(R.id.total);
            tv.setText("Total: " + Double.toString(totalDbl));
            if(totalDbl > 0){
                tv.setTextColor(Color.GREEN);
            }
            else{
                tv.setTextColor(Color.RED);
            }
            progresssDialog.hide();
            progresssDialog.dismiss();
        }
    }

}
