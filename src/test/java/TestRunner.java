import com.intuit.karate.junit5.Karate;

class TestRunner {
//    @Karate.Test
//    Karate testGet() {
//        return Karate.run("apis/features/GetRequest").relativeTo(getClass());
//    }

//    @Karate.Test
//    Karate testTags() {
//        return Karate.run("apis/features/GetRequest").tags("@GetDelayedResponse").relativeTo(getClass());
//    }

    @Karate.Test
    Karate runAllTests() {
        return Karate.run(
                "apis/features/GetRequest",
                "apis/features/PostRequest",
                "apis/features/PutRequest",
                "apis/features/DeleteRequest"
        ).relativeTo(getClass());
    }
}
// Grade Command to run
// ./gradlew test --tests TestRunner
// ./gradlew test --tests ParallelRunner
// ./gradlew test --tests ParallelRunner -d
