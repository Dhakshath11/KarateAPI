import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class ParallelRunner {

    @Test
    void testParallel() {
        //Results results = Runner.path("classpath:apis/features").tags("@GetDelayedResponse").parallel(5); Only GetDelayedResponse
        //Results results = Runner.path("classpath:apis/features").tags("~@GetDelayedResponse").parallel(5); Avoid GetDelayedResponse
        Results results = Runner.path("classpath:apis/features").parallel(5);
        assertEquals(0, results.getFailCount(), results.getErrorMessages());
    }

}
