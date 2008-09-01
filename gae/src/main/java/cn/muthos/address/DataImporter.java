package cn.muthos.address;

import java.io.InputStreamReader;
import java.io.Reader;
import java.util.ArrayList;
import java.util.List;

import org.restlet.Client;
import org.restlet.data.Protocol;
import org.restlet.data.Response;
import org.restlet.data.Status;
import org.restlet.ext.json.JsonRepresentation;

import au.com.bytecode.opencsv.bean.ColumnPositionMappingStrategy;
import au.com.bytecode.opencsv.bean.CsvToBean;

public class DataImporter {
	@SuppressWarnings("unchecked")
	public void importData() throws Exception {
		ColumnPositionMappingStrategy strat = new ColumnPositionMappingStrategy();
		strat.setType(Area.class);
		String[] columns = new String[] { "code", "name", "parentArea", "unit",
				"middle" }; // the fields to bind do in your JavaBean
		strat.setColumnMapping(columns);

		Client client = new Client(Protocol.HTTP);
		Reader reader = new InputStreamReader(this.getClass()
				.getResourceAsStream("areas.csv"));
		CsvToBean csv = new CsvToBean();
		List<Area> areas = csv.parse(strat, reader);
		List<String> errorCodes = new ArrayList<String>();
		int count = 0;
		for (Area area : areas) {
			Response response = client.put("http://localhost:8080/areas/"
					+ area.getCode() + "/", new JsonRepresentation(area));
			System.out.println(++count + ":" + area.getCode());
			System.out.println(response.getEntity().getText());
			if (response.getStatus() ==  Status.SERVER_ERROR_INTERNAL) {
				errorCodes.add(area.getCode());
			}
			Thread.sleep(2000);
		}
		System.out.println(errorCodes);
	}

	public static void main(String[] args) throws Exception {
		new DataImporter().importData();
	}
}
