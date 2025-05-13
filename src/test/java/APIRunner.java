import com.intuit.karate.junit5.Karate;

class APIRunner {
    @Karate.Test
    Karate run() {
        String karateOptions = System.getProperty("karate.options");
        System.out.println(karateOptions);
        if (karateOptions != null && !karateOptions.isEmpty()) {
            // Removing ".relativeTo(getClass());" to avoid appending of automatic /src/test/resources into path
            // If we enable it, then we need to pass classpath & only relative path
            // Command ==> ./gradlew test --tests APIRunner  -Dkarate.options="classpath:apis/features/DeleteRequest.feature:10" -d
            //return Karate.run(karateOptions.split(" ")).relativeTo(getClass());
            return Karate.run(karateOptions.split(" "));
        } else {
            return Karate.run().relativeTo(getClass());
        }
    }
}

// ./gradlew test --tests APIRunner  -Dkarate.options="src/test/resources/apis/features/DeleteRequest.feature:10" -d
// Supports One scenario at time; Can go with hyperExecuete to distribute scenarios