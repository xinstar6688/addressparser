package cn.muthos.address.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.http.client.URL;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class Index {
	private static final String JSON_URL = GWT.getModuleBaseURL();
	private Label label = new Label();
	private VerticalPanel resultPanel = new VerticalPanel();

	private JsonHandler addressHandler = new JsonHandler() {
		public void handleJsonResponse(JavaScriptObject jso) {
			resultPanel.clear();

			if (jso == null) {
				displayError("Couldn't retrieve JSON");
				return;
			}

			try {
				// parse the response text into JSON
				JSONObject jsonObject = new JSONObject(jso);
				JSONArray jsonArray = jsonObject.get("areas").isArray();

				StringBuffer result = new StringBuffer();
				for (int i = 0; i < jsonArray.size(); i++) {
					JSONObject area = jsonArray.get(i).isObject();
					resultPanel.add(new Label(area.get("address").isString().stringValue()));
				}

				label.setText(result.toString());
			} catch (JSONException e) {
				displayError("Could not parse JSON");
			}
		}
	};
	
	public void onModuleLoad() {
		VerticalPanel vPanel = new VerticalPanel();
		vPanel.setSpacing(50);
		vPanel.setSize(Window.getClientWidth() - 100 + "px", Window
				.getClientHeight()
				- 100 + "px");
		vPanel.setHorizontalAlignment(VerticalPanel.ALIGN_CENTER);
		vPanel.setVerticalAlignment(VerticalPanel.ALIGN_TOP);
		RootPanel.get().add(vPanel);

		HorizontalPanel hPanel = new HorizontalPanel();
		vPanel.add(hPanel);

		final TextBox text = new TextBox();
		hPanel.add(text);
		Button button = new Button("Parse It");
		hPanel.add(button);

		vPanel.add(label);
		vPanel.add(resultPanel);

		button.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				String url = URL.encode(JSON_URL + "/parse?q=" + text.getText()
						+ "&callback=");
				getJson(url, addressHandler);
			}
		});
	}

	private void displayError(String message) {
		label.setText(message);
	}

	public native static void getJson(String url, JsonHandler handler) /*-{
	   if (!window["callbacks"]) {
	       window["callbacks"] = {};
	   }	   
	   var callbacks = window["callbacks"];
	   
	   var uid = (new Date()).getTime();
	   var uid_done = uid + "done";

	   var script = document.createElement("script");
	   script.setAttribute("src", url+"callbacks[" + uid + "]");
	   script.setAttribute("type", "text/javascript");
	   script.charset = "utf-8"
	   
	   callbacks[uid] = function(jsonObj) {
	     handler.@cn.muthos.address.client.JsonHandler::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;)(jsonObj);
	     callbacks[uid_done] = true;
	   }
	   
	   // JSON download has 1-second timeout
	   setTimeout(function() {
	     if (!callbacks[uid_done]) {
	       handler.@cn.muthos.address.client.JsonHandler::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;)(null);
	     } 

	     // cleanup
	     document.body.removeChild(script);
	     delete callbacks[uid];
	     delete callbacks[uid_done];
	   }, 5000);
	   
	   document.body.appendChild(script);
	}-*/;
}
