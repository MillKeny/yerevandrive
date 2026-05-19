state("Yerevan Drive")
{
	byte ops : 0xDC5FC;
	byte trans : 0xB1230, 0x198;
	byte inmenu : 0xAF794;
}

startup {
	settings.Add("mode", false, "Is your transmission Manual?");
}

split {
	if (timer.CurrentPhase.ToString() != "NotRunning" && current.inmenu == 1) {
		return true;
	}
}

start {
	if (timer.CurrentPhase.ToString() == "NotRunning") {
		if (!settings["mode"] && old.trans == 1 && current.trans == 2) return true;
		else if (settings["mode"] && current.inmenu == 0) return true;
	}
}