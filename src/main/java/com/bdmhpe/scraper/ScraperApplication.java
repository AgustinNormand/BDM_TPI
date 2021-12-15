package com.bdmhpe.scraper;

import org.apache.commons.cli.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ScraperApplication implements CommandLineRunner {

	@Autowired
	AuthService authService;
	private Options options;

	public static void main(String[] args) {
		SpringApplication.run(ScraperApplication.class, args);
	}

	@Override
	public void run(String... args) throws Exception {
		options = buildOptions();

		try {
			CommandLineParser parser = new DefaultParser();
			CommandLine cmd = parser.parse(options, args);

			AuthorizationInfo code = authService.authorize(cmd.getOptionValue("code"));
			System.out.println(code.prettyPrint());
		}
		catch (MissingOptionException e){
			HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("scraper", options);
		}
	}

	private Options buildOptions() {
		Options options = new Options();
		Option codeOption = new Option("c", "code", true, "MELI code to be used for auth");
		codeOption.setType(String.class);
		options.addOption(codeOption);
		return options;
	}
}
