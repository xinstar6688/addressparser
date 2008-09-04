package cn.muthos.address.client;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.http.client.URL;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;
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
public class Index implements JsonHandler {
	private static final List<String> excludeAreas = new ArrayList<String>();
	private static final String JSON_URL = "http://address.muthos.cn/parse?q=";
	private int jsonRequestId = 0;
	private Label label = new Label();

	static {
		excludeAreas.add("市辖区");
		excludeAreas.add("所属县");
	}
	
	public void onModuleLoad() {
		VerticalPanel vPanel = new VerticalPanel();
		vPanel.setSpacing(50);
		vPanel.setSize(Window.getClientWidth() - 100 + "px", 
				Window.getClientHeight() - 100 + "px");
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

		button.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				String url = URL.encode(JSON_URL + text.getText()
						+ "&callback=");
				getJson(jsonRequestId++, url, Index.this);
			}
		});
	}

	private void displayError(String message) {
		label.setText(message);
	}
	
	
	private String getAreaName(JSONObject area) {
		String name = area.get("name").isString().stringValue();
		if (excludeAreas.contains(name)) {
			name = "";
		}
		JSONValue parent = area.get("parentArea");
		if (parent == null) {
			return name;
		}
		return getAreaName(parent.isObject()) + name;
	}

	public void handleJsonResponse(JavaScriptObject jso) {
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
				if (i > 0) {
					result.append("/");
				}
				JSONObject area = jsonArray.get(i).isObject();
				result.append(getAreaName(area));
			}

			label.setText(result.toString());
		} catch (JSONException e) {
			displayError("Could not parse JSON");
		}
	}

	public native static void getJson(int requestId, String url,
			JsonHandler handler) /*-{
	   var callback = "callback" + requestId;
	   
	   var script = document.createElement("script");
	   script.setAttribute("src", url+callback);
	   script.setAttribute("type", "text/javascript");

	   window[callback] = function(jsonObj) {
	     handler.@cn.muthos.address.client.JsonHandler::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;)(jsonObj);
	     window[callback + "done"] = true;
	   }
	   
	   // JSON download has 1-second timeout
	   setTimeout(function() {
	     if (!window[callback + "done"]) {
	       handler.@cn.muthos.address.client.JsonHandler::handleJsonResponse(Lcom/google/gwt/core/client/JavaScriptObject;)(null);
	     } 

	     // cleanup
	     document.body.removeChild(script);
	     delete window[callback];
	     delete window[callback + "done"];
	   }, 2000);
	   
	   document.body.appendChild(script);
	}-*/;
}
