package cn.muthos.address;

public class Area {
	private String code;
	private String name;
	private String middle;
	private String unit;
	private String parentArea;

	public String getCode() {
		return code;
	}

	public String getName() {
		return name;
	}

	public String getMiddle() {
		return middle;
	}

	public String getUnit() {
		return unit;
	}

	public String getParentArea() {
		return parentArea;
	}

	public void setCode(String code) {
		this.code = code;
	}

	public void setName(String name) {
		this.name = name;
	}

	public void setMiddle(String middle) {
		this.middle = middle;
	}

	public void setUnit(String unit) {
		this.unit = unit;
	}

	public void setParentArea(String parentArea) {
		this.parentArea = parentArea;
	}
}
