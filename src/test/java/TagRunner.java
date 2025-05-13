import com.intuit.karate.junit5.Karate;

import java.util.Optional;

public class TagRunner {

    @Karate.Test
    Karate testTagged() {
        System.out.println("Passed value : " + System.getProperty("karate.options"));
        String tag = Optional.ofNullable(System.getProperty("karate.options"))
                .filter(s -> !s.trim().isEmpty())
                .orElse("~@no_tag");

        System.out.println("Running Karate tests with tag: " + tag);
        return Karate.run().tags(tag).relativeTo(getClass());
    }
}

// Single Tag ==> ./gradlew test --tests TagRunner -Dkarate.options="--tags @GetRequest"
// Multi Tag  ==> ./gradlew test --tests TagRunner -Dkarate.options="--tags @GetRequest,@PutRequest"
// Debug Mode ==> ./gradlew test --tests TagRunner -Dkarate.options="--tags @GetRequest,@PutRequest" -d